from .Gus import Client

class BacklogClient(Client):
    '''
    Module to interact with work on the backlog
    '''
    def mark_work_fixed(self, work_id, build_id):
        '''
        Sets status to fixed on the specified work item.  Requires a scheduled build when marking fixed
        '''
        self.sf_session.ADM_Work__c.update(work_id, {'Status__c': 'Fixed', 'Scheduled_Build__c': build_id})

    def mark_work_in_progress(self, work_id):
        '''
        Sets status of specified work item to 'In Progress'
        '''
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
        '''
        Adds a comment to the specified work item
        '''
        self.sf_session.ADM_Comment__c.create({
            'Work__c': work_id,
            'Body__c': comment,
        })
        
    def add_collab_link(self, work, link):
        '''
        Adds a link to a code review to the comment and related URL field on a work item if the related URL field is blank
        '''
        if work['Related_URL__c'] == '' or work['Related_URL__C'] is None:
            self.sf_session.ADM_Work__c.update(work['Id'], {'Related_URL__c': link})
            
        self.add_comment(work['Id'], 'Code Review Created: %s' % link)
        
    def get_open_work_for_user_id(self, user_id):
        '''
        Returns a list of work that is assigned to a specified user and not 'resolved'
        '''
        try:
            result = self.sf_session.query("select Name, Status__c, Subject__c from ADM_Work__c where Assignee__c = '%s' and Resolved__c = 0" % user_id)
            out = []
            for record in result['records']:
                out.append((record['Name'], record['Status__c'], record['Subject__c']))
        except:
            out = None
            
        return out
    
    def get_in_progress_work_for_user_id(self, user_id):
        '''
        Returns a list of work that is assigned to a specified user and status 'In Progress'
        '''
        try:
            result = self.sf_session.query("select Name, Status__c, Subject__c from ADM_Work__c where Assignee__c = '%s' and Status__c = 'In Progress'" % user_id)
            out = []
            for record in result['records']:
                out.append((record['Name'], record['Status__c'], record['Subject__c']))
        except:
            out = None
            
        return out
    
    def get_work_with_active_tasks_for_user(self, user_id):
        '''
        Returns a list of unresolved work items that have tasks assigned to the specified user where
        the tasks are not complete
        '''
        result = self.sf_session.query("select Work__c from ADM_Task__c where Assigned_To__c='%s' and Status__c!='Completed'"  % user_id)
        out = []
        for record in result['records']:
            if record['Work__c'] not in [x[0] for x in out]:
                data = self.sf_session.ADM_Work__c.get(record['Work__c'])
                if data['Resolved__c'] == 0:
                    out.append((data['Name'], data['Status__c'], data['Subject__c']))
            
        return out
    
    def get_work_for_sprint(self, sprintid):
        '''
        Returns a list of unresolved work in the specifed sprint
        '''
        result = self.sf_session.query("select Name, Status__c, Subject__c from ADM_Work__c where Sprint__c='%s' and Resolved__c = 0" % sprintid)
        out = []
        for record in result['records']:
            out.append((record['Name'], record['Status__c'], record['Subject__c']))
            
        return out
    
    def get_open_work_for_user(self, email):
        '''
        returns a list of open work by email instead of user id
        '''
        user_id = self.get_user_id_for_email(email)
        return self.get_open_work_for_user_id(user_id)
        
    def get_sprint_work_for_teams(self, user_id):
        '''
        Returns a list of unresolved work in the current sprint for all teams that a user is assigned to
        '''
        teams = self.get_scrum_teams_for_user(user_id)
        sprint_work = []
        for team in teams:
            current_sprint = self.get_current_sprint_for_team(team[0])
            if current_sprint is not None:
                team_sprint_work = self.get_work_for_sprint(current_sprint)
                for w in team_sprint_work:
                    sprint_work.append(w)
                    
        return sprint_work

    
    def get_potential_work_for_user(self, user_id):
        '''
        Returns a list of work that is: a) assigned to the specified user b) assigned to the current sprint for all
        teams that the use is a member of and c) has uncompleted tasks assigned to the user
        '''
        out = []
        # get in progress work
        in_progress = self.get_in_progress_work_for_user_id(user_id)
        
        # get work in sprint
        sprint_work = self.get_sprint_work_for_teams(user_id)

        # get work with tasks assigned
        task_work = self.get_work_with_active_tasks_for_user(user_id)
        
        for w in in_progress:
            out.append(w)
            
        for w in sprint_work:
            if w[0] not in [x[0] for x in out] and w[1] == 'In Progress':
                out.append(w)
        
        for w in task_work:
            if w[0] not in [x[0] for x in out]:
                out.append(w)
                
        return out
    
