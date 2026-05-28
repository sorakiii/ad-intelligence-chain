<!-- 
  @file 团队卡片组件
  @description 展示AI超级战队的信息卡片
-->
<template>
  <div class="team-card">
    <!-- 操作按钮 -->
    <div class="card-actions">
      <button class="action-btn">✏️</button>
      <button class="action-btn">📋</button>
      <button class="action-btn">🗑️</button>
    </div>

    <!-- 团队信息 -->
    <div class="team-icon">{{ icon }}</div>
    <h3 class="team-title">{{ title }}</h3>
    <p class="team-desc">{{ description }}</p>

    <!-- 成员列表 -->
    <div class="team-members">
      <div 
        v-for="member in members" 
        :key="member.role"
        class="member-tag"
      >
        {{ member.role }}
      </div>
    </div>

    <!-- 标签列表 -->
    <div class="team-tags">
      <span 
        v-for="tag in tags" 
        :key="tag"
        class="tag"
      >
        {{ tag }}
      </span>
    </div>

    <!-- 统计信息 -->
    <div class="team-stats">
      <div class="stat-item">
        <span class="stat-icon">📊</span>
        <span>使用次数: {{ useCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-icon">⭐️</span>
        <span>评分: {{ rating }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: String,
  title: String,
  description: String,
  memberCount: Number,
  rating: Number,
  members: {
    type: Array,
    default: () => []
  },
  features: {
    type: Array,
    default: () => []
  },
  tags: {
    type: Array,
    default: () => []
  },
  useCount: Number
})

defineEmits(['start-project'])
</script>

<style scoped>
.team-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
  position: relative;
}

.card-actions {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--bg-color);
}

.team-icon {
  width: 48px;
  height: 48px;
  background: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  margin-bottom: 16px;
}

.team-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.team-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.team-members {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
}

.member-tag {
  padding: 6px 12px;
  background: rgba(0, 102, 255, 0.1);
  color: var(--primary-color);
  border-radius: 6px;
  font-size: 13px;
  text-align: center;
}

.team-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag {
  padding: 4px 12px;
  background: var(--bg-color);
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.team-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--text-secondary);
}

.stat-icon {
  font-size: 14px;
}
</style> 