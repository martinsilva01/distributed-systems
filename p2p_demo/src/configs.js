import * as vNG from "v-network-graph";
import { ForceLayout } from "v-network-graph/lib/force-layout";

export function configs() {
  return vNG.defineConfigs({
    view: {
      layoutHandler: new ForceLayout()
    },

    node: {
      label: { visible: true }
    },

    edge: {
      normal: {
        width: ({ edgeWidth }) => edgeWidth,
        color: (edge) => `hsl(${edge.hue}, 50%, 50%`
      },

      hover: {
        width: 8,
        color: (edge) => `hsl(${edge.hue}, 50%, 50%`
      }
    }
  });
}
