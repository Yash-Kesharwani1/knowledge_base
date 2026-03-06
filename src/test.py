import json
import re

# with open("data/jobs_final.json", "r") as f:
#     jobs = json.load(f)
#     cnt=0
#     python_jobs=[]
#     for job in jobs:
#         if re.search(r"Python", job["jobRole"]):
#             python_jobs.append(job)
#             cnt+=1
#     print(cnt)
#     with open("data/python_jobs.json", "w") as f:
#         json.dump(python_jobs, f, indent=4)

with open("data/python_jobs.json", "r") as f:
    jobs = json.load(f)
    
    with open("data/python_jobs_test.json", "w") as f:
        for i in range(0, 5):
            json.dump(jobs[i], f, indent=4)
            f.write(",")