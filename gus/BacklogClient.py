from .Gus import Client, NoRecordException
from .GusSession import GusSession

class BacklogClient(Client):
    def find_build_id(self, build_name):
        result = self.sf_session.query("select Id from ADM_Build__c where Name='%s'" % build_name)
        try:
            build_id = result["records"][0]["Id"]
        except:
            raise NoRecordException('Can\'t find build ' + build_name)

        return build_id

    def find_work(self, work_name):
        result = self.sf_session.query("select Id from ADM_Work__c where Name='%s'" % work_name)
        try:
            work_id = result["records"][0]["Id"]
            work = self.sf_session.ADM_Work__c.get(work_id)
        except:
            raise NoRecordException('Can\'t find work ' + work_name)

        return work

    def mark_work_fixed(self, work_id, build_id):
        self.sf_session.ADM_Work__c.update(work_id, {'Status__c': 'Fixed', 'Scheduled_Build__c': build_id})

    def mark_work_in_progress(self, work_id):
        self.sf_session.ADM_Work__c.update(work_id, {'Status__c': 'In Progress'})

    def create_changelist(self, work_id, changelist_url, author, title, commit_message, files_changed):
        changes = ''
        for change in files_changed:
            changes = changes + change.path + "\n"
            
        self.add_changelist_comment(work_id, commit_message, files_changed)
        
    def add_changelist_comment(self, work_id, commit_message, changes):
        body = "COMMIT DETAILS\n--------------------------\n\n%s\n\n%s" % (commit_message, changes)
        self.add_comment(work_id, body)
        
    def add_comment(self, work_id, comment):
        self.sf_session.ADM_Comment__c.create({
            'Work__c': work_id,
            'Body__c': comment,
        })
        
    def add_collab_link(self, work, link):
        if work['Related_Url__c'] == '':
            self.sf_session.ADM_Work__c.update(work['Id'], {'Related_Url__c': link})
            
        self.add_comment(work['Id'], 'Code Review Created: %s' % link)
        
    def get_open_work_for_user(self, email):
        user_id = self.get_user_id_for_email(email)
        return self.get_open_work_for_user_id(user_id)
        
    def get_open_work_for_user_id(self, user_id):
        try:
            result = self.sf_session.query("select Name, Status__c, Subject__c from ADM_Work__c where Assignee__c = '%s' and Resolved__c = 0" % user_id)
            out = []
            for record in result['records']:
                out.append((record['Name'], record['Status__c'], record['Subject__c']))
        except:
            out = None
            
        return out
    
    def get_work_with_active_tasks_for_user(self, user_id):
        result = self.sf_session.query("select Work__c from ADM_Task__c where Assigned_To__c='%s' and Status__c!='Completed'"  % user_id)
        out = []
        for record in result['records']:
            if record['Work__c'] not in [x[0] for x in out]:
                data = self.sf_session.ADM_Work__c.get(record['Work__c'])
                if data['Resolved__c'] == 0:
                    out.append((data['Name'], data['Status__c'], data['Subject__c']))
            
        return out
    