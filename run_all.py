import os, subprocess, sys, time, webbrowser, signal
root=os.path.dirname(os.path.abspath(__file__))
env=os.environ.copy();env.setdefault('API_URL','http://127.0.0.1:8080')
api=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8080'],cwd=root,env=env)
time.sleep(3)
ui=subprocess.Popen([sys.executable,'-m','streamlit','run','app/ui.py','--server.address','127.0.0.1','--server.port','8501'],cwd=root,env=env)
time.sleep(3);webbrowser.open('http://127.0.0.1:8501')
print('JIT-Flow UI: http://127.0.0.1:8501 | API: http://127.0.0.1:8080/docs | Durdur: Ctrl+C')
try: ui.wait()
except KeyboardInterrupt: pass
finally:
    for p in (ui,api):
        if p.poll() is None:p.terminate()
