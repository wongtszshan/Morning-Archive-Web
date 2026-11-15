import argparse, datetime as dt, json, re, os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAT=ROOT/"reports/catalog.json"
PIN=ROOT/"reports/protected.json"
LOG=ROOT/"reports/cleanup-log.json"
DAYS={"global":30,"semiconductor":90,"premarket":14}
def read(p,default): return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
def write(p,data): p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def run():
 p=argparse.ArgumentParser()
 p.add_argument("--mode",choices=["cleanup","delete","protect","unprotect"],required=True)
 p.add_argument("--ids",default="")
 p.add_argument("--apply",action="store_true")
 a=p.parse_args()
 cat=read(CAT,{})
 if not isinstance(cat.get("reports"),list): raise ValueError("Invalid catalog")
 entries=cat["reports"]; known={}
 for item in entries:
  rid=item.get("id",""); url=item.get("url",""); category=item.get("category",""); date=item.get("date","")
  m=re.fullmatch(r"reports/(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})-(global|semiconductor|premarket)\.html",url)
  if not m or rid!=date+"-"+category or m.group(3)!=date or m.group(4)!=category or rid in known: raise ValueError("Invalid report metadata "+rid)
  day=dt.date.fromisoformat(date)
  if m.group(1)!=str(day.year) or m.group(2)!=f"{day.month:02d}": raise ValueError("Invalid month "+rid)
  file=ROOT/url
  if not file.is_file(): raise ValueError("Missing file "+url)
  known[rid]=(item,day,file)
 pins=read(PIN,{"ids":[]})
 protected=set(pins["ids"])
 if any(not re.fullmatch(r"\d{4}-\d{2}-\d{2}-(global|semiconductor|premarket)",x) for x in protected): raise ValueError("Invalid protected IDs")
 ids=set(filter(None,re.split(r"[,;\s]+",a.ids.strip())))
 if a.mode!="cleanup" and (not ids or ids-known.keys()): raise ValueError("Unknown/missing IDs "+str(sorted(ids-known.keys())))
 today=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date()
 selected=[]
 if a.mode=="cleanup":
  selected=sorted(rid for rid,(item,day,_) in known.items() if day<=today and (today-day).days>DAYS[item["category"]] and rid not in protected)
 elif a.mode=="delete":
  if ids & protected: raise ValueError("Protected IDs: "+str(sorted(ids&protected)))
  selected=sorted(ids)
 elif a.mode=="protect": protected|=ids
 elif a.mode=="unprotect": protected-=ids
 summary=["Mode: "+a.mode,"SGT date: "+str(today),"Apply: "+str(a.apply),"Indexed: "+str(len(entries)),"Delete candidates: "+str(len(selected))]
 summary += ["DELETE "+rid for rid in selected]
 if a.mode in ("protect","unprotect"): summary += [a.mode.upper()+" "+x for x in sorted(ids)]
 if a.apply:
  if selected:
   for rid in selected: known[rid][2].unlink()
   cat["reports"]=[entry for entry in entries if entry["id"] not in selected]
   cat["updated_at"]=dt.datetime.now(dt.timezone.utc).isoformat()
   write(CAT,cat)
  if a.mode in ("protect","unprotect"): write(PIN,{"ids":sorted(protected)})
  if selected or a.mode in ("protect","unprotect"):
   log=read(LOG,{"events":[]})
   log["events"].insert(0,{"at":dt.datetime.now(dt.timezone.utc).isoformat(),"mode":a.mode,"deleted":selected,"changed_ids":sorted(ids)})
   log["events"]=log["events"][:100];write(LOG,log)
 msg="APPLIED" if a.apply else "PREVIEW ONLY"
 print(msg+"\n"+"\n".join(summary))
 if os.environ.get("GITHUB_STEP_SUMMARY"):
  with open(os.environ["GITHUB_STEP_SUMMARY"],"a",encoding="utf-8") as f:f.write("### "+msg+"\n\n"+"".join("- "+s+"\n" for s in summary))
if __name__=="__main__": run()
