from threading import Thread
import Task


num_tasks = int(input("Enter the number of tasks to run: "))


link = input("Enter the url of the product: ")
size_wanted = input("Enter the desired size: ")
username = input("Enter your username: ")
password = input("Enter your password: ")

task_arr = [Task(link, size_wanted, username, password)] * num_tasks

i = 0
running_threads = []

while task_arr:
    if len(running_threads == 4): # cap of four threads
        for thread in running_threads:
            thread.start()
        for thread in running_threads:
            thread.join()
        running_threads.clear()
    else:
        running_threads.append(Thread(target=task_arr.pop().run()))

for thread in running_threads:
    thread.start()
for thread in running_threads:
    thread.join()

print("All tasks have been run.")
