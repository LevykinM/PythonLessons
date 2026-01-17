from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import os

TASKS_FILE = "tasks.txt"

TASKS = []
NEXT_TASK_ID = 1


def save_tasks():
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(TASKS, f, ensure_ascii=False)


def load_tasks():
    global TASKS, NEXT_TASK_ID
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            TASKS = json.load(f)

        if TASKS:
            NEXT_TASK_ID = max(t["id"] for t in TASKS) + 1


class SimpleRESTHandler(BaseHTTPRequestHandler):
    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length > 0 else b""
        if not raw:
            return None
        try:
            return json.loads(raw)
        except:
            return None

    def _send_json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _error(self, status, msg):
        self._send_json({"error": msg}, status=status)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/tasks":
            self._send_json(TASKS, status=200)
        else:
            self._error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)

        if parsed.path == "/tasks":
            self.create_task()
            return

        # /tasks/<id>/complete
        if parsed.path.startswith("/tasks/") and parsed.path.endswith("/complete"):
            self.complete_task(parsed.path)
            return

        self._error(404, "Not found")

    def create_task(self):
        global NEXT_TASK_ID

        data = self._read_json_body()
        if not data:
            return self._error(400, "JSON body is required")

        if "title" not in data or "priority" not in data:
            return self._error(400, "Fields 'title' and 'priority' are required")

        title = data["title"]
        priority = data["priority"]

        if priority not in ("low", "normal", "high"):
            return self._error(400, "priority must be one of: low, normal, high")

        task = {
            "id": NEXT_TASK_ID,
            "title": title,
            "priority": priority,
            "isDone": False
        }

        NEXT_TASK_ID += 1
        TASKS.append(task)
        save_tasks()

        self._send_json(task, status=200)

    def complete_task(self, path):
        # path like: /tasks/12/complete
        parts = path.split("/")
        # ["", "tasks", "12", "complete"]

        if len(parts) != 4:
            self.send_response(404)
            self.end_headers()
            return

        try:
            task_id = int(parts[2])
        except:
            self.send_response(404)
            self.end_headers()
            return

        for task in TASKS:
            if task["id"] == task_id:
                task["isDone"] = True
                save_tasks()
                self.send_response(200)
                self.end_headers()
                return

        self.send_response(404)
        self.end_headers()


def run():
    load_tasks()
    server = HTTPServer(("", 8000), SimpleRESTHandler)
    print("Server started on port 8000")
    server.serve_forever()


if __name__ == "__main__":
    run()
