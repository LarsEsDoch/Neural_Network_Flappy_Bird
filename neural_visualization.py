import pygame
import math


def draw_neural_network(win, net, inputs, x_offset=650, y_offset=50):
    if not hasattr(net, 'nodes') or not hasattr(net, 'connections'):
        return

    layer_sizes = [3]

    hidden_nodes = []
    for node_id in net.nodes:
        if node_id not in net.input_nodes and node_id not in net.output_nodes:
            hidden_nodes.append(node_id)

    if hidden_nodes:
        layer_sizes.append(len(hidden_nodes))
    layer_sizes.append(1)

    node_radius = 15
    layer_spacing = 120
    node_spacing = 50

    node_positions = {}
    layer_nodes = {}

    input_y_start = y_offset + 100
    for i, node_id in enumerate(net.input_nodes):
        node_positions[node_id] = (x_offset, input_y_start + i * node_spacing)
        layer_nodes.setdefault(0, []).append(node_id)

    if hidden_nodes:
        hidden_y_start = y_offset + 100
        for i, node_id in enumerate(hidden_nodes):
            node_positions[node_id] = (x_offset + layer_spacing, hidden_y_start + i * node_spacing)
            layer_nodes.setdefault(1, []).append(node_id)

    layer_offset = 2 if hidden_nodes else 1
    output_y = y_offset + 150
    for i, node_id in enumerate(net.output_nodes):
        node_positions[node_id] = (x_offset + layer_spacing * layer_offset, output_y)
        layer_nodes.setdefault(layer_offset, []).append(node_id)

    for conn in net.connections.values():
        if not conn.enabled:
            continue

        from_node = conn.key[0]
        to_node = conn.key[1]

        if from_node not in node_positions or to_node not in node_positions:
            continue

        from_pos = node_positions[from_node]
        to_pos = node_positions[to_node]

        weight = conn.weight
        if weight > 0:
            color = (0, min(255, int(weight * 100)), 0)
        else:
            color = (min(255, int(abs(weight) * 100)), 0, 0)

        thickness = max(1, min(5, int(abs(weight) * 2)))

        pygame.draw.line(win, color, from_pos, to_pos, thickness)

    for layer, nodes in layer_nodes.items():
        for node_id in nodes:
            pos = node_positions[node_id]

            if node_id in net.values:
                activation = net.values[node_id]

                intensity = min(255, int(abs(activation) * 255))
                if activation > 0:
                    color = (0, intensity, 0)
                else:
                    color = (intensity, 0, 0)
            else:
                color = (100, 100, 100)

            pygame.draw.circle(win, color, pos, node_radius)
            pygame.draw.circle(win, (255, 255, 255), pos, node_radius, 2)

            font = pygame.font.SysFont("comicsans", 12)
            id_text = font.render(str(node_id), 1, (255, 255, 255))
            win.blit(id_text, (pos[0] - id_text.get_width() // 2, pos[1] - id_text.get_height() // 2))

    font = pygame.font.SysFont(None, 16)

    input_labels = ["Bird Y", "To Top", "To Bottom"]
    for i, (node_id, label) in enumerate(zip(net.input_nodes, input_labels)):
        pos = node_positions[node_id]
        label_text = font.render(label, 1, (255, 255, 255))
        win.blit(label_text, (pos[0] - label_text.get_width() - 25, pos[1] - 8))

        if i < len(inputs):
            value_text = font.render(f"{inputs[i]:.1f}", 1, (200, 200, 200))
            win.blit(value_text, (pos[0] + node_radius + 5, pos[1] - 8))

    for node_id in net.output_nodes:
        pos = node_positions[node_id]
        label_text = font.render("Jump", 1, (255, 255, 255))
        win.blit(label_text, (pos[0] + node_radius + 5, pos[1] - 8))

        if node_id in net.values:
            value_text = font.render(f"{net.values[node_id]:.3f}", 1, (200, 200, 200))
            win.blit(value_text, (pos[0] - value_text.get_width() - 25, pos[1] - 8))