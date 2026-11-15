import datetime as dt, json, subprocess, sys, tempfile, unittest
from pathlib import Path

SCRIPT=Path(__file__).resolve().parents[1]/"scripts/manage_reports.py"
class MaintenanceTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)
  (self.root/"scripts").mkdir()
  (self.root/"reports/2020/01").mkdir(parents=True)
  (self.root/"scripts/manage_reports.py").write_text(SCRIPT.read_text(encoding="utf-8"),encoding="utf-8")
  self.id="2020-01-01-global"
  self.url="reports/2020/01/2020-01-01-global.html"
  (self.root/self.url).write_text("<html>Example</html>",encoding="utf-8")
  self.catalog=self.root/"reports/catalog.json"
  self.catalog.write_text(json.dumps({"reports":[{"id":self.id,"url":self.url,"date":"2020-01-01","category":"global","title":"Example"}]}))
  (self.root/"reports/protected.json").write_text('{"ids":[]}')
 def call(self,mode,apply=False,ids=""):
  return subprocess.run([sys.executable,str(self.root/"scripts/manage_reports.py"),"--mode",mode,"--ids",ids]+(["--apply"] if apply else []),capture_output=True,text=True)
 def test_preview_does_not_delete(self):
  x=self.call("cleanup")
  self.assertEqual(x.returncode,0,x.stderr)
  self.assertTrue((self.root/self.url).exists())
  self.assertEqual(len(json.loads(self.catalog.read_text())["reports"]),1)
 def test_manual_delete_updates_catalog(self):
  x=self.call("delete",True,self.id)
  self.assertEqual(x.returncode,0,x.stderr)
  self.assertFalse((self.root/self.url).exists())
  self.assertEqual(json.loads(self.catalog.read_text())["reports"],[])
 def test_protected_report_not_deleted(self):
  self.assertEqual(self.call("protect",True,self.id).returncode,0)
  x=self.call("cleanup",True)
  self.assertEqual(x.returncode,0,x.stderr)
  self.assertTrue((self.root/self.url).exists())
  self.assertNotEqual(self.call("delete",True,self.id).returncode,0)
 def test_auto_cleanup(self):
  x=self.call("cleanup",True)
  self.assertEqual(x.returncode,0,x.stderr)
  self.assertFalse((self.root/self.url).exists())
 def test_unknown_id_rejected(self):
  self.assertNotEqual(self.call("delete",True,"2020-01-02-global").returncode,0)
if __name__=="__main__": unittest.main()
