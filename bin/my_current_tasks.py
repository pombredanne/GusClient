from gus.TaskClient import TaskClient

def main():
    gus = TaskClient()
    tasks = gus.find_my_tasks()


if __name__ == '__main__':
    main()