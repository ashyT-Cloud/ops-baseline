# Runbook

Operational playbook for Ops Baseline. Written for someone under time pressure — exact commands, minimal explanation. SSH access: `ssh -i ~/.ssh/ops-baseline ubuntu@<public_ip>` (get the IP with `terraform output public_ip` from `terraform/`).

---

## Scenario 1: App is down / `AppDown` alert fired

**Check**

```bash
cd ~/ops-baseline
docker compose ps app
curl -i localhost/health
```

If `app` isn't `Up (healthy)`, or the curl fails/times out, the app is genuinely down.

**Diagnose**

```bash
docker compose logs app --tail 50
docker compose ps db      # a down DB can crash-loop the app on startup
```

**Fix**

```bash
docker compose up -d app
# if that doesn't recover it:
docker compose up -d --build app
```

**Verify**

```bash
docker compose ps app                 # should show healthy
curl -i localhost/health              # should return 200 OK
```

Check Prometheus confirms recovery, and that a `RESOLVED` email follows within ~2 minutes:

```bash
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

---

## Scenario 2: Disk is full / `HighDiskUsage` alert fired

**Check**

```bash
df -h /
```

Confirm usage is genuinely above 80% — the alert fires at that threshold, sustained for 2 minutes.

**Diagnose — find what's actually using the space**

```bash
sudo du -sh /var/lib/docker/* 2>/dev/null | sort -rh | head -10
docker system df
```

Common causes on this box: old Docker images/build cache piling up, or Postgres's data volume growing.

**Fix**

```bash
# reclaim space from unused Docker images/containers/build cache (safe — doesn't touch running containers)
docker system prune -af

# check again
df -h /
```

If that's not enough, check `/var/log` for oversized logs, and check for any leftover manual test files (e.g. `/var/tmp/fill.img` from a deliberate drill — see below):

```bash
ls -lh /var/tmp/
sudo rm -f /var/tmp/fill.img    # only if this file exists from a prior manual test
```

**Verify**

```bash
df -h /                                # should be back under 80%
curl -s localhost:9090/api/v1/alerts | python3 -m json.tool | grep -E '"alertname"|"state"'
```

Confirm a `RESOLVED: HighDiskUsage` email arrives within a couple of minutes.

---

## Scenario 3: Database needs restoring from a backup

Use this after data loss, corruption, or a bad migration — anything where the current database state is wrong and a known-good backup exists in S3.

**Check what backups are available**

```bash
cd ~/ops-baseline
aws s3 ls s3://ops-baseline-backups-487054650859/postgres/ --region us-east-1
```

**Restore the latest backup**

```bash
./scripts/restore.sh
```

To restore a *specific* (not latest) backup instead:

```bash
./scripts/restore.sh appdb-20260921T122115Z.sql.gz
```

**Verify**

```bash
curl -s localhost/history
```

Confirm the data matches what's expected. If the app was serving errors before the restore, also recheck:

```bash
docker compose ps app
curl -i localhost/health
```

**If you need to back up *before* making a risky change** (always do this first):

```bash
./scripts/backup.sh
```

---

## General escalation

If none of the above resolves it:

1. Check all containers: `docker compose ps`
2. Check disk, memory, load: `df -h /`, `free -h`, `uptime`
3. Full restart of the core stack (data persists in the Docker volume):
```bash
   docker compose down
   docker compose up -d
```
4. If the instance itself is unresponsive, check it's running in the AWS console, then reboot from there if needed. Terraform state is unaffected by an instance reboot.
5. As a last resort, infrastructure is fully reproducible:
```bash
   cd terraform
   terraform apply    # recreates anything drifted or destroyed
```
   Then redeploy the app: `git pull && docker compose up -d --build app` on the (possibly new) instance.
