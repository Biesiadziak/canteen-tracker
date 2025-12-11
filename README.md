# Canteen Tracker

A web application that tracks the canteen menu, translates it, and extracts dishes using AI.

## 🚀 Quick Start

### Manual Run
```bash
cd /home/esa5/site/canteen-tracker
source venv/bin/activate
python backend/app.py
```
The site will be available at `http://localhost:8000`.

### Using the Startup Script
This script kills any existing process on port 8000 and starts the app in the background.
```bash
./start.sh
```

---

## ⚙️ System Service (Auto-start)

The application is configured to run as a systemd service named `canteen.service`.

### Manage the Service
```bash
# Start the service
sudo systemctl start canteen.service

# Stop the service
sudo systemctl stop canteen.service

# Restart the service
sudo systemctl restart canteen.service

# Check status
sudo systemctl status canteen.service
```

### View Logs
To see the output logs from the service:
```bash
# Follow logs in real-time
journalctl -u canteen.service -f
```

---

## 🛠️ Maintenance & Debugging

### Force Menu Rescan
If the menu hasn't updated, you can force a rescan via the API:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"force": true}' http://localhost:8000/api/check-now
```

### Check Logs (Manual Run)
If running manually or via `start.sh`, logs are written to `backend.log`:
```bash
tail -f backend.log
```

### Accessing from Network
To access the site from other devices on the same network, use the server's IP address:
```
http://<YOUR_IP_ADDRESS>:8000
```
Find your IP address with:
```bash
hostname -I
```

---

## 📦 Installation (First Time Setup)

1. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   Create a `.env` file in the root directory with your API keys:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Setup System Service**
   ```bash
   sudo ln -s /home/esa5/site/canteen-tracker/canteen.service /etc/systemd/system/canteen.service
   sudo systemctl daemon-reload
   sudo systemctl enable canteen.service
   sudo systemctl start canteen.service
   ```
