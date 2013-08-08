from gus.Gus import Client

class TaskClient(Client):
    def find_my_tasks(self):
        userid = self.get_current_user_id()
        result = self.sf_session.query("select Name, Subject__c")
        
    def find_my_current_tasks(self):
        userid = self.get_current_user_id()
        teams = self.get_scrum_teams_for_user(userid)
        out = []
        for team in teams:
            current_sprint = self.get_current_sprint_for_team(team[0])
            tasks = self.find_tasks_for_user_in_sprint(userid, current_sprint)
            for item in tasks:
                out.append(item)

        return out

    def find_tasks_for_user_in_sprint(self, userid, sprintid):
        pass