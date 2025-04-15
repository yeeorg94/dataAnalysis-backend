CREATE TABLE IF NOT EXISTS event_tracking (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY COMMENT '自增主键',
    user_id BIGINT UNSIGNED DEFAULT NULL COMMENT '用户ID（可选）',
    source_platform ENUM('pc', 'h5', 'mini_program', 'android', 'ios') NOT NULL COMMENT '来源平台',
    event_type VARCHAR(100) NOT NULL COMMENT '埋点类型',
    ip_address VARBINARY(16) NOT NULL COMMENT 'IP地址（支持IPv6）',
    user_agent VARCHAR(500) DEFAULT NULL COMMENT '用户代理信息',
    referrer VARCHAR(1000) DEFAULT NULL COMMENT '来源页面',
    event_params JSON NOT NULL COMMENT '扩展参数（JSON格式）',
    created_at DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3) COMMENT '事件时间（精确到毫秒）',
    
    INDEX idx_source_platform (source_platform),
    INDEX idx_event_type (event_type),
    INDEX idx_created_at (created_at),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='埋点事件跟踪表'; 