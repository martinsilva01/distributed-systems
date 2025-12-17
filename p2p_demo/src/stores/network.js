import { defineStore } from "pinia";

export const useNetworkStore = defineStore('network', {
  state: () => ({
    nodes: {},
    edges: {}
  }),
  actions: {
    addNode(data) {
      this.nodes[data.peer_id] = { name: data.role, size: 20, color: "blue" };
    },
    addEdge(peer_id, neighbor_id) {
      const edgeId = `${peer_id}_${neighbor_id}`;
      if (!this.edges[edgeId]) {
        this.edges[edgeId] = { source: peer_id, target: neighbor_id, color: "gray", width: 10 };
      }
    }
  }
});
