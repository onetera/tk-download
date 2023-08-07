# :coding: utf-8

class Task:
    def __init__(self, _shot_id, _sg):
        self.get_task(_shot_id,_sg)

    def get_task(self,id,_sg):
        print(id)
        filters = [
            ["entity", "is", {"type": "Shot", "id": id}]
        ]
        fields = ["id", "content", "sg_status_list"]
        self._tasks = _sg.find("Task", filters, fields)

    @property
    def tasks(self):
        return self._tasks
    
