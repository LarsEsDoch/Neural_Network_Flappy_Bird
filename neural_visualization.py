import pygame
import neat


def draw_neural_network(win, genome, config, inputs, x_offset=650, y_offset=50, horizontal_spacing=150):
    if not genome or not config:
        return

    input_nodes = [-1, -2, -3]
    output_nodes = [0]

    hidden_nodes = []
    for node_id in genome.nodes.keys():
        if node_id not in input_nodes and node_id not in output_nodes:
            hidden_nodes.append(node_id)

    hidden_nodes.sort()

    node_radius = 15
    layer_spacing = horizontal_spacing
    node_spacing = 60

    node_positions = {}

    layers = organize_into_layers(genome, input_nodes, output_nodes, hidden_nodes)

    max_nodes_in_layer = max([len(layer) for layer in layers]) if layers else 1
    total_height = max_nodes_in_layer * node_spacing

    for layer_idx, layer in enumerate(layers):
        x_pos = x_offset + layer_idx * layer_spacing
        layer_height = len(layer) * node_spacing
        start_y = y_offset + (total_height - layer_height) / 2 + 100

        for i, node_id in enumerate(layer):
            node_positions[node_id] = (int(x_pos), int(start_y + i * node_spacing))

    node_values = calculate_node_activations(genome, config, inputs, input_nodes, hidden_nodes, output_nodes, layers)

    for conn_key, conn in genome.connections.items():
        if not conn.enabled:
            continue

        from_node = conn_key[0]
        to_node = conn_key[1]

        if from_node not in node_positions or to_node not in node_positions:
            continue

        from_pos = node_positions[from_node]
        to_pos = node_positions[to_node]

        weight = conn.weight

        if weight > 0:
            color = (0, min(255, int(abs(weight) * 30 + 50)), 0)
        else:
            color = (min(255, int(abs(weight) * 30 + 50)), 0, 0)

        thickness = max(1, min(4, int(abs(weight) * 0.8 + 1)))

        pygame.draw.line(win, color, from_pos, to_pos, thickness)

        mid_x = (from_pos[0] + to_pos[0]) // 2
        mid_y = (from_pos[1] + to_pos[1]) // 2
        weight_font = pygame.font.SysFont(None, 12)
        weight_text = weight_font.render(f"{weight:.1f}", 1, (180, 180, 180))

        bg_rect = weight_text.get_rect(center=(mid_x, mid_y - 10))
        bg_rect.inflate_ip(4, 2)
        pygame.draw.rect(win, (40, 40, 40), bg_rect)
        win.blit(weight_text, (mid_x - weight_text.get_width() // 2, mid_y - 10))

    for node_id, pos in node_positions.items():
        if node_id in node_values:
            activation = node_values[node_id]
            normalized = max(-1, min(1, activation))
            intensity = min(255, int(abs(normalized) * 200 + 55))
            if normalized > 0:
                color = (0, intensity, 0)
            elif normalized < 0:
                color = (intensity, 0, 0)
            else:
                color = (100, 100, 100)
        else:
            color = (100, 100, 100)

        pygame.draw.circle(win, color, pos, node_radius)
        pygame.draw.circle(win, (255, 255, 255), pos, node_radius, 2)

        font = pygame.font.SysFont(None, 13)
        id_text = font.render(str(node_id), 1, (255, 255, 255))
        win.blit(id_text, (pos[0] - id_text.get_width() // 2, pos[1] - id_text.get_height() // 2))

    label_font = pygame.font.SysFont(None, 16)
    value_font = pygame.font.SysFont(None, 14)

    input_labels = ["Bird Y", "To Top", "To Bot"]
    for i, (node_id, label) in enumerate(zip(input_nodes, input_labels)):
        if node_id in node_positions:
            pos = node_positions[node_id]
            label_text = label_font.render(label, 1, (255, 255, 255))
            win.blit(label_text, (pos[0] - label_text.get_width() - 30, pos[1] - 8))

            if i < len(inputs):
                value_text = value_font.render(f"{inputs[i]:.0f}", 1, (200, 200, 200))
                win.blit(value_text, (pos[0] + node_radius + 8, pos[1] - 7))

    for node_id in output_nodes:
        if node_id in node_positions:
            pos = node_positions[node_id]
            label_text = label_font.render("Jump", 1, (255, 255, 255))
            win.blit(label_text, (pos[0] + node_radius + 8, pos[1] - 8))

            if node_id in node_values:
                value_text = value_font.render(f"{node_values[node_id]:.3f}", 1, (200, 200, 200))
                win.blit(value_text, (pos[0] - value_text.get_width() - 30, pos[1] - 7))

    if hidden_nodes:
        for node_id in hidden_nodes:
            if node_id in node_positions and node_id in node_values:
                pos = node_positions[node_id]
                value_text = value_font.render(f"{node_values[node_id]:.2f}", 1, (180, 180, 180))

                bg_rect = value_text.get_rect(center=(pos[0], pos[1] + node_radius + 8))
                bg_rect.inflate_ip(4, 2)
                pygame.draw.rect(win, (40, 40, 40), bg_rect)
                win.blit(value_text, (pos[0] - value_text.get_width() // 2, pos[1] + node_radius + 5))

    layer_font = pygame.font.SysFont(None, 14)
    layer_names = ["Input", "Hidden", "Output"] if len(layers) == 3 else \
        ["Input"] + [f"H{i}" for i in range(1, len(layers) - 1)] + ["Output"] if len(layers) > 3 else \
            ["Input", "Output"]

    for layer_idx, (layer, name) in enumerate(zip(layers, layer_names)):
        if layer:
            x_pos = x_offset + layer_idx * layer_spacing
            layer_text = layer_font.render(name, 1, (150, 150, 150))
            win.blit(layer_text, (x_pos - layer_text.get_width() // 2, y_offset + 70))

    if hasattr(genome, 'fitness') and genome.fitness is not None:
        fitness_font = pygame.font.SysFont(None, 16)
        fitness_text = fitness_font.render(f"Fitness: {genome.fitness:.1f}", 1, (255, 215, 0))
        win.blit(fitness_text, (x_offset, y_offset + 20))

    enabled_connections = sum(1 for conn in genome.connections.values() if conn.enabled)
    total_connections = len(genome.connections)
    conn_font = pygame.font.SysFont(None, 14)
    conn_text = conn_font.render(f"Connections: {enabled_connections}/{total_connections}", 1, (200, 200, 200))
    win.blit(conn_text, (x_offset, y_offset + 40))

    node_text = conn_font.render(f"Nodes: {len(genome.nodes)} ({len(hidden_nodes)} hidden)", 1, (200, 200, 200))
    win.blit(node_text, (x_offset, y_offset + 55))


def organize_into_layers(genome, input_nodes, output_nodes, hidden_nodes):
    if not hidden_nodes:
        return [input_nodes, output_nodes]

    connections = {}
    for conn_key, conn in genome.connections.items():
        if conn.enabled:
            from_node, to_node = conn_key
            if to_node not in connections:
                connections[to_node] = []
            connections[to_node].append(from_node)

    node_layers = {}

    for node in input_nodes:
        node_layers[node] = 0

    unprocessed = set(hidden_nodes + output_nodes)
    max_iterations = 100
    iteration = 0

    while unprocessed and iteration < max_iterations:
        iteration += 1
        made_progress = False

        for node in list(unprocessed):
            if node in connections:
                input_layers = []
                all_assigned = True
                for input_node in connections[node]:
                    if input_node in node_layers:
                        input_layers.append(node_layers[input_node])
                    else:
                        all_assigned = False
                        break

                if all_assigned and input_layers:
                    node_layers[node] = max(input_layers) + 1
                    unprocessed.remove(node)
                    made_progress = True
            else:
                node_layers[node] = 1
                unprocessed.remove(node)
                made_progress = True

        if not made_progress:
            next_layer = max(node_layers.values()) + 1 if node_layers else 1
            for node in unprocessed:
                node_layers[node] = next_layer
            break

    max_layer = max(node_layers.values()) if node_layers else 1
    layers = [[] for _ in range(max_layer + 1)]

    for node, layer in node_layers.items():
        layers[layer].append(node)

    return [layer for layer in layers if layer]


def calculate_node_activations(genome, config, inputs, input_nodes, hidden_nodes, output_nodes, layers):
    node_values = {}

    for i, node_id in enumerate(input_nodes):
        if i < len(inputs):
            node_values[node_id] = inputs[i] / 500.0

    for layer in layers[1:]:
        for node_id in layer:
            if node_id not in genome.nodes:
                continue

            node = genome.nodes[node_id]

            activation_sum = node.bias

            for conn_key, conn in genome.connections.items():
                if not conn.enabled:
                    continue

                from_node, to_node = conn_key
                if to_node == node_id and from_node in node_values:
                    activation_sum += node_values[from_node] * conn.weight

            import math
            node_values[node_id] = math.tanh(activation_sum)

    try:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        output = net.activate(inputs)
        if output_nodes[0] in node_values:
            node_values[output_nodes[0]] = output[0]
    except:
        pass

    return node_values