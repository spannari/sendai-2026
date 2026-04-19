# Docker Disk Cleanup Checklist

This checklist provides a structured approach for identifying and reclaiming disk space used by Docker. It is intended as a practical reference for routine maintenance.

---

## 1. Check current disk usage

Run the following command to see how disk space is distributed:

```bash
docker system df
```

This shows usage by images, containers, volumes, and build cache.

---

## 2. Remove unused containers, networks, and dangling images

```bash
docker system prune
```

This removes:

* Stopped containers
* Unused networks
* Dangling images

Warning: This does not remove all images or volumes.

---

## 3. Remove all unused images

```bash
docker system prune -a
```

This additionally removes:

* All images not currently used by a container

Warning: Images will need to be re-pulled or rebuilt when needed again.

---

## 4. Remove unused volumes

```bash
docker volume prune
```

This removes volumes not attached to any container.

Warning: Volumes may contain persistent data such as databases or application state. Data loss is permanent.

---

## 5. Perform full cleanup (use with caution)

```bash
docker system prune -a --volumes
```

This removes:

* All unused containers
* All unused images
* All unused networks
* All unused volumes

Warning: This command can delete important data. Ensure no required data is stored in volumes before running.

---

## 6. Clean build cache

```bash
docker builder prune
```

Optional deeper cleanup:

```bash
docker builder prune -a
```

This removes cached image layers created during builds.

---

## 7. Inspect volumes manually

List all volumes:

```bash
docker volume ls
```

Inspect a volume:

```bash
docker volume inspect VOLUME_NAME
```

Use this to identify volumes that may still contain important data.

---

## 8. Inspect containers and their attached volumes

List all containers:

```bash
docker ps -a
```

Inspect a container:

```bash
docker inspect CONTAINER_ID
```

Check the "Mounts" section to see which volumes are in use.

---

## 9. Periodic maintenance recommendation

Run the following regularly in development environments:

```bash
docker system prune
```

Perform deeper cleanup only when disk space is limited.

---

## 10. What does not require manual cleanup

The following are managed automatically or typically negligible:

* Running containers
* Active images used by containers
* Docker networks (unless excessive accumulation occurs)
* Docker system files inside the internal storage directory

Do not manually delete files from Docker’s internal storage paths such as `/var/lib/docker`.

---

## 11. Notes for Docker Desktop users

Docker Desktop stores data inside a virtual disk image. Even after cleanup, disk space may not immediately shrink at the operating system level.

Use Docker Desktop settings to manage disk usage if necessary.

---

## Summary

1. Check usage with `docker system df`
2. Run `docker system prune` for routine cleanup
3. Use `-a` and `--volumes` only when necessary
4. Always verify volumes before deletion

This checklist should be followed carefully to avoid unintended data loss.
