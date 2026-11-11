-- ПР7. Именованные запросы исполняются из этого файла.
-- Параметры :id, :query и другие передаются отдельно от SQL.

-- 1. Список пользователей, включая пользователей без доступа.
-- name: users
SELECT id, username, full_name, email FROM users ORDER BY full_name, id;

-- 2. Список проектов с владельцами — JOIN.
-- name: projects
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email
FROM projects p JOIN users o ON o.id = p.owner_id
ORDER BY p.opened_on, p.id;

-- 3. Проект по идентификатору — WHERE и JOIN.
-- name: project_detail
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email
FROM projects p JOIN users o ON o.id = p.owner_id
WHERE p.id = :id;

-- 4. Список репозиториев с LIMIT и OFFSET.
-- name: repositories
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private
FROM repositories r
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
ORDER BY r.name COLLATE NOCASE, r.id
LIMIT :limit OFFSET :offset;

-- 5. Репозиторий и его проект с владельцем.
-- name: repository_detail
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private
FROM repositories r
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
WHERE r.id = :id;

-- 6. Репозитории выбранного проекта.
-- name: project_repositories
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private
FROM repositories r
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
WHERE p.id = :id ORDER BY r.name COLLATE NOCASE, r.id;

-- 7. Все записи доступа с пользователями и репозиториями.
-- name: members
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private,
       m.id AS member_id, m.role, m.is_revoked,
       u.id AS user_id, u.username, u.full_name, u.email
FROM members m
JOIN repositories r ON r.id = m.repo_id
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
JOIN users u ON u.id = m.user_id
ORDER BY m.id;

-- 8. Связанная информация о конкретной записи доступа.
-- name: member_detail
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private,
       m.id AS member_id, m.role, m.is_revoked,
       u.id AS user_id, u.username, u.full_name, u.email
FROM members m
JOIN repositories r ON r.id = m.repo_id
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
JOIN users u ON u.id = m.user_id
WHERE m.id = :id;

-- 9. Участники репозитория, включая отозванные доступы.
-- name: repository_members
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private,
       m.id AS member_id, m.role, m.is_revoked,
       u.id AS user_id, u.username, u.full_name, u.email
FROM members m
JOIN repositories r ON r.id = m.repo_id
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
JOIN users u ON u.id = m.user_id
WHERE r.id = :id ORDER BY m.id;

-- 10. Только активные записи доступа — WHERE.
-- name: active_members
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private,
       m.id AS member_id, m.role, m.is_revoked,
       u.id AS user_id, u.username, u.full_name, u.email
FROM members m
JOIN repositories r ON r.id = m.repo_id
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
JOIN users u ON u.id = m.user_id
WHERE m.is_revoked = 0 ORDER BY u.full_name, m.id;

-- 11. Поиск по имени, видимости и отсутствию активного доступа.
-- name: search_repositories
SELECT p.id AS project_id, p.title, p.opened_on,
       o.id AS owner_id, o.username AS owner_username,
       o.full_name AS owner_full_name, o.email AS owner_email,
       r.id AS repo_id, r.name AS repo_name, r.clone_url, r.private
FROM repositories r
JOIN projects p ON p.id = r.project_id
JOIN users o ON o.id = p.owner_id
WHERE r.name LIKE :query ESCAPE '\'
  AND (:private IS NULL OR r.private = :private)
  AND (:user_id IS NULL OR NOT EXISTS (
      SELECT 1 FROM members m
      WHERE m.repo_id = r.id AND m.user_id = :user_id
        AND m.is_revoked = 0
  ))
ORDER BY r.name COLLATE NOCASE, r.id;

-- 12. Агрегаты COUNT, SUM по режимам доступа.
-- name: repository_summary
SELECT COUNT(*) AS total,
       COALESCE(SUM(private), 0) AS private_count,
       COUNT(*) - COALESCE(SUM(private), 0) AS public_count
FROM repositories;

-- 13. Подсчёт активных и отозванных доступов.
-- name: member_summary
SELECT COUNT(*) AS total,
       COALESCE(SUM(is_revoked = 0), 0) AS active_count,
       COALESCE(SUM(is_revoked), 0) AS revoked_count
FROM members;

-- 14. LEFT JOIN и GROUP BY: активные участники, включая ноль.
-- name: repository_statistics
SELECT r.id, r.name, COUNT(m.id) AS active_count
FROM repositories r
LEFT JOIN members m ON m.repo_id = r.id AND m.is_revoked = 0
GROUP BY r.id, r.name
ORDER BY active_count DESC, r.name, r.id;

-- 15. GROUP BY: распределение активных доступов по ролям.
-- name: role_statistics
SELECT role, COUNT(*) AS member_count
FROM members WHERE is_revoked = 0
GROUP BY role ORDER BY member_count DESC, role;

-- 16. HAVING: репозитории с числом участников выше порога.
-- name: popular_repositories
SELECT r.id, r.name, COUNT(m.id) AS active_count
FROM repositories r
LEFT JOIN members m ON m.repo_id = r.id AND m.is_revoked = 0
GROUP BY r.id, r.name
HAVING COUNT(m.id) > :min_members
ORDER BY active_count DESC, r.name, r.id;

-- 17. GROUP BY: количество репозиториев по проектам.
-- name: project_statistics
SELECT p.id, p.title, COUNT(r.id) AS repo_count
FROM projects p LEFT JOIN repositories r ON r.project_id = p.id
GROUP BY p.id, p.title ORDER BY repo_count DESC, p.id;

-- 18. Контроль количества импортированных записей.
-- name: counts
SELECT (SELECT COUNT(*) FROM users) AS users,
       (SELECT COUNT(*) FROM projects) AS projects,
       (SELECT COUNT(*) FROM repositories) AS repositories,
       (SELECT COUNT(*) FROM members) AS members;
