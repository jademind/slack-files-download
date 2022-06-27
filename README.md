# Slack File Downloads

---

Downloads all files of messages of your Slack (workspace) JSON export. Each channel will be processed and a separate
folder (default=files) gets created containing all files.

This helps to back up all your files when if you are going to close your Slack account. The script checks if the file
was already downloaded, so you can also use it to create incremental backups.

### How to use

```bash
# Start file downloads with export directory
./slack-files-download.py ~/Downloads/SlackExport/

# Start file downloads with alternate output dir
./slack-files-download.py --output export ~/Downloads/SlackExport/

# Display help message
./slack-files-download.py -h
```
