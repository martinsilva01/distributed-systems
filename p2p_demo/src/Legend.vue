<template>
  <div class="legend">
    <div class="legend-item" v-for="item in items" :key="item.label">
      <span class="color-box" :style="{ backgroundColor: item.color }" />
      <span>{{ item.label }}</span>
    </div>
  </div>
</template>

<script setup>
const items = [
  { label: "REQ", color: "blue" },
  { label: "REPLY", color: "purple" },
  { label: "JOB", color: "yellow" },
  { label: "SUCCESS", color: "green" },
  { label: "No traffic", color: "gray" },
]
</script>

<style scoped>
.legend {
  display: flex;
  gap: 14px;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  border-radius: 6px;
  font-size: 14px;
  align-items: center;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.color-box {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid #3334;
}
</style>
