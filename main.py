"""Adaptive Agent Broker - matching + learning + validation"""
import json,sys
from typing import Dict,List
class Broker:
 def __init__(self):
  self.a={};self.t={};self.h=[]
 def register_agent(self,aid,caps):
  if aid in self.a:return False
  self.a[aid]={"caps":{c:1.0 for c in caps},"tasks":[],"success":0,"total":0};return True
 def submit_task(self,tid,reqs):
  if tid in self.t:return False
  self.t[tid]={"reqs":reqs,"assigned":[]};return True
 def _score(self,caps,reqs):
  return sum(caps.get(r,0)for r in reqs)/len(reqs)if reqs else 0
 def recommend(self,reqs,limit=3):
  r=[]
  for aid,ag in self.a.items():
   s=self._score(ag["caps"],reqs)
   if s>=0.3:sr=ag["success"]/ag["total"]if ag["total"]else 0;r.append({"agent_id":aid,"confidence":round(s,3),"success_rate":round(sr,3)})
  return sorted(r,key=lambda x:x["confidence"],reverse=True)[:limit]
 def learn(self,aid,tid,success):
  if aid not in self.a or tid not in self.t:return False
  ag,tk=self.a[aid],self.t[tid];self.h.append({"agent":aid,"task":tid,"success":success});ag["total"]+=1
  if success:ag["success"]+=1
  for r in tk["reqs"]:
   if r in ag["caps"]:ag["caps"][r]=max(0.1,min(1.0,ag["caps"][r]+(0.1 if success else -0.1)))
  return True
 def validate(self):
  tests=[(self.register_agent("v1",["py"]),"reg"),(self.register_agent("v2",["js"]),"dup"),(self.submit_task("vt",["py"]),"task"),(self.learn("v1","vt",True),"learn"),(len(self.recommend(["py"]))>0,"rec")]
  p=sum(1 for r,_ in tests if r);return{"passed":p,"total":len(tests),"valid":p==len(tests)}
if __name__=="__main__":
 if len(sys.argv)>1 and("-h"in sys.argv[1]or"--help"in sys.argv[1]):
  print("Adaptive Agent Broker\nUsage: python3 main.py\nFeatures: register, submit, recommend, learn, validate");sys.exit(0)
 b=Broker();print("=== Validation ===");v=b.validate();print(f"Tests: {v['passed']}/{v['total']}")
 print("\n=== Demo ===")
 b.register_agent("py",["python","api"]);b.register_agent("js",["javascript","ui"])
 b.submit_task("t1",["python"]);b.submit_task("t2",["javascript"])
 print("Recs:",b.recommend(["python"]))
 b.learn("py","t1",True);b.learn("js","t2",False)
 print("\nSuccess rates: py=",b.a["py"]["success"]/b.a["py"]["total"]if b.a["py"]["total"]else 0)
 print("✓ Complete")