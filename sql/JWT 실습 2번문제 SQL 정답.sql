
-- 상위 리뷰어 목록 가져오는 SQL

SELECT *
FROM (SELECT 
        r.user_id,
        u.nickname,
        COUNT(*) as review_count,
        AVG(r.rating) as average_rating,
        MAX(r.created_at) as last_review_date
    FROM review r
    JOIN user u ON r.user_id = u.id
    GROUP BY r.user_id, u.nickname ) as reviewer_stat
ORDER BY review_count DESC, average_rating DESC
LIMIT 10;



-- 기간별 리뷰 통계 SQL (3개 입니다.)
-- 1. 전체 통계
SELECT 
    COUNT(*) as review_count,
    ROUND(AVG(rating), 1) as average_rating
FROM review
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';

-- 2. 일자별 통계
SELECT 
    DATE(created_at) as date,
    COUNT(*) as review_count,
    ROUND(AVG(rating), 1) as average_rating
FROM review
WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 3. 카테고리별 통계
SELECT 
    rt.category,
    COUNT(r.id) as review_count,
    ROUND(AVG(r.rating), 1) as average_rating
FROM review r
JOIN restaurant rt ON r.restaurant_id = rt.id
WHERE r.created_at BETWEEN :startDate AND :endDate
GROUP BY rt.category
ORDER BY review_count DESC;



-- 인기 음식점 목록 가져오는 SQL

SELECT *
FROM  (
        SELECT 
            r.id as restaurant_id,
            r.name,
            r.category,
            COUNT(rv.id) as review_count,
            ROUND(AVG(rv.rating), 1) as average_rating,
            MAX(rv.created_at) as last_review_date
        FROM restaurant r
        LEFT JOIN review rv ON r.id = rv.restaurant_id
        WHERE r.category = '한식'
        GROUP BY r.id, r.name, r.category
        HAVING COUNT(rv.id) >= 1
    ) as restaurant_stat
ORDER BY review_count DESC, average_rating DESC



