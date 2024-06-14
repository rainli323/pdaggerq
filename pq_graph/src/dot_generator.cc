#include "../include/pq_graph.h"
using namespace pdaggerq;

// Function to join the labels of lines with a specified delimiter
string join(const vector<Line> &lines, const string &delimiter) {
    std::stringstream result;
    // Iterate through the lines and concatenate their labels with the delimiter
    for (size_t i = 0; i < lines.size(); ++i) {
        result << lines[i].label_;
        if (i < lines.size() - 1) result << delimiter;  // Add delimiter between labels
    }
    return result.str();
}

// Function to format the label for a term
string format_label(const Term &term) {
    std::stringstream label;
    int w = minimum_precision(term.coefficient_);  // Determine the precision for the coefficient

    // Add coefficient to the label if it's not 1.0
    if (term.coefficient_ != 1.0)
        label << (term.coefficient_ == -1.0 ? "-" : to_string_with_precision(term.coefficient_, w) + " ");

    // Add permutations to the label
    for (const auto &perm : term.term_perms())
        label << "P(" << perm.first << "," << perm.second << ") ";

    // Get vertices from the term's linkage
    vector<ConstVertexPtr> vertices = term.term_linkage()->vertices(true);

    // Add each vertex and its lines to the label
    for (const auto &vertex : vertices) {
        if (vertex && !vertex->empty()) {
            label << vertex->base_name_;
            if (!vertex->lines().empty()) label << "(" << join(vertex->lines(), ",") << ")";
            label << " ";
        }
    }
    return label.str();  // Return the formatted label as a string
}


void PQGraph::write_dot(string &filepath) {
    cout << "Writing DOT file to " << filepath << endl;
    ofstream os(filepath);
    os << "digraph G {\n";
    string padding = "    ";

    size_t term_count = 0;

    // Graph attributes
    os << padding << "rankdir=RL;\n";      // Set graph direction from right to left
    os << padding << "mode=hier;\n";       // Set hierarchical mode for layout
    os << padding << "compound=true;\n";   // Treat subgraphs as separate graphs
    os << padding << "splines=spline;\n";  // Use spline edges
    os << padding << "dim=2;\n";           // Set graph dimension to 2
    os << padding << "normalize=true;\n";  // Normalize node coordinates
    os << padding << "K=1.0;\n";           // Set spring constant for layout
    os << padding << "node [fontname=\"Helvetica\"];\n";  // Set node font
    os << padding << "edge [concentrate=false, len=1.5];\n";       // Do not concentrate edges

    padding += "    ";
    for (auto &it : equations_) {
        Equation &eq = it.second;
        if (eq.terms().empty()) continue;

        string graphname = "cluster_equation_" + it.first;
        os << padding << "subgraph " << graphname << " {\n";
        os << padding << "    style=rounded;\n";       // Rounded style for subgraph
        os << padding << "    clusterrank=local;\n";   // Local clustering rank (no global ordering)
        eq.write_dot(os, term_count, "black");         // Write the equation's terms to the DOT file

        // Write the assignment vertex to the DOT file
        const auto vertex = eq.assignment_vertex();
        os << padding << "label = \"" << vertex->base_name_;
        if (!vertex->lines().empty()) os << "(" << join(vertex->lines(), ",") << ")";
        os << "\";\n";

        os << padding << "color = \"black\";\n";       // Set color of subgraph border
        os << padding << "fontsize = 32;\n";           // Set font size for label
        os << padding << "}\n";
    }
    os << "}\n";
    os.close();

    cout << "DOT file written successfully!" << endl;
    cout << "Run the following command to generate the graph:" << endl;
    cout << "       dot -Tpdf -O " << filepath << endl;
    cout << "For a more compact graph, run the following command:" << endl;
    cout << "       fdp -Tpdf -O " << filepath << endl;
}

ostream &Equation::write_dot(ostream &os, size_t &term_count, const string &color) {
    string padding = "        ";
    size_t term_id = 0, dummy_count = 0;

    // Iterate through each term in the equation
    for (Term &term : terms_) {
        if (term.rhs().empty()) continue;  // Skip terms with empty right-hand side

        term.compute_scaling(true);  // Compute scaling for the term
        string graphname = "cluster_term" + to_string(term_count++);  // Generate unique name for the subgraph
        os << padding << "subgraph " << graphname << " {\n";
        os << padding << "    style=rounded;\n";  // Rounded style for subgraph
        os << padding << "    clusterrank=local;\n";  // Local clustering rank
        os << padding << "    label=\"" << format_label(term) << "\";\n";  // Set label for the subgraph

        // Write the linkage of the term to the DOT file
        term.term_linkage()->write_dot(os, term_id, dummy_count, color);
        os << padding << "}\n";
    }
    return os;
}

string determine_direction(bool o, bool curr_is_bra) {
    // determine direction of edge based on whether current edge is bra or ket
    if (curr_is_bra)
         return o ? "forward" : "back";
    else return o ? "back" : "forward";
}

// Function to append null nodes for external lines in the graph
void append_null_nodes(const ConstLinkagePtr &link, const vector<ConstVertexPtr> &vertices, size_t &dummy_count, size_t term_id, vector<string> &null_nodes, vector<string> &ext_edge_names, size_t &group_count, const string &ext_edge_style, const string &null_node_style) {
    for (const auto &line : link->lines_) {
        if (line.sig_) continue;  // Skip lines marked as significant

        // Create a unique identifier for the null node
        string null_node = "null_node" + to_string(dummy_count++) + (line.o_ ? "o" : "v") + line.label_;
        bool added_null = false;

        // Iterate through each vertex to find where to add the null node
        for (size_t i = 0; i < vertices.size(); ++i) {
            const auto &current = vertices[i];
            if (current->base_name().empty()) continue;  // Skip vertices with empty base name

            const auto &current_lines = current->lines();
            auto curr_it = find(current_lines.begin(), current_lines.end(), line);
            if (curr_it == current_lines.end()) continue;  // Skip if the line is not found in the current vertex

            // Add the null node to the graph if not already added
            if (!added_null) {
                null_nodes.push_back(null_node + " [label=\"\", " + null_node_style + ", group=" + to_string(group_count++) + "];\n");
                added_null = true;
            }

            // Determine the direction of the edge
            string direction = determine_direction(line.o_, curr_it < current_lines.end() - current_lines.size() / 2);
            // Create the connection string for the edge
            string connnection = (curr_it < current_lines.end() - current_lines.size() / 2 ? current->base_name() + "_" + to_string(i) + to_string(term_id) : null_node) + " -> " + (curr_it < current_lines.end() - current_lines.size() / 2 ? null_node : current->base_name() + "_" + to_string(i) + to_string(term_id));
            // Add the edge to the list of external edge names
            ext_edge_names.push_back(connnection + " [label=\"" + line.label_ + "\"," + ext_edge_style + ", dir=" + direction + "];\n");
        }
    }
}

// Function to append edge links between vertices in the graph
void append_edge_links(const ConstLinkagePtr &link, const ConstVertexPtr &current, const ConstVertexPtr &next, const string &current_node, const string &next_node, vector<string> &int_edge_names, const string &int_edge_style) {
    const auto &current_lines = current->lines();  // Get lines from the current vertex
    size_t current_len = current_lines.size();

    // Iterate through internal lines in the linkage
    for (const auto &line : link->int_lines()) {
        string edge_label = line.label_;  // Get label for the edge
        auto curr_it = find(current_lines.begin(), current_lines.end(), line);
        size_t curr_dist = distance(current_lines.begin(), curr_it);
        bool curr_is_bra = curr_dist < current_len - current_len / 2;  // Determine if the current line is a bra
        string direction = determine_direction(line.o_, curr_is_bra);  // Determine the direction of the edge
        // Create the connection string for the edge
        string connnection = (curr_is_bra ? next_node : current_node) + " -> " + (curr_is_bra ? current_node : next_node);
        // Add the edge to the list of internal edge names
        int_edge_names.push_back(connnection + " [label=\"" + edge_label + "\"," + int_edge_style + ", dir=" + direction + "];\n");
    }
}


// Function to append edges between vertices
void append_edges(const vector<ConstVertexPtr> &vertices, const ConstVertexPtr &current, size_t i, vector<string> &int_edge_names, const string &l_id, size_t term_id, const string &int_edge_style) {
    string current_node = current->base_name() + "_" + l_id;  // Current node identifier

    // Iterate through remaining vertices to find edges
    for (size_t j = i + 1; j < vertices.size(); ++j) {
        const auto &next = vertices[j];
        if (next->base_name().empty()) continue;  // Skip vertices with empty base name

        string r_id = to_string(j) + to_string(term_id);  // Next node identifier
        string next_node = next->base_name() + "_" + r_id;  // Next node identifier string

        // Get the linkage between current and next vertices and append edge links
        const auto &link = as_link(current * next);
        append_edge_links(link, current, next, current_node, next_node, int_edge_names, int_edge_style);
    }
}

// Function to sort vertices based on their base name
vector<ConstVertexPtr> sorted_vertices(const ConstLinkagePtr& link) {
    vector<ConstVertexPtr> vertices = link->vertices();  // Get vertices from linkage
    sort(vertices.begin(), vertices.end(), [](const ConstVertexPtr &a, const ConstVertexPtr &b) {
        return a->base_name() < b->base_name();  // Sort vertices by base name
    });
    return vertices;
}

// Function to sort temporary vertices based on their base name
vector<ConstVertexPtr> sorted_temp_vertices(const ConstLinkagePtr& link) {
    vector<ConstVertexPtr> temp_verts;

    // Collect temporary vertices from linkage
    for (const auto &temp : link->link_vector(false)) {
        if (temp->is_temp()) {
            for (const auto &temp_vert : as_link(temp)->vertices()) {
                temp_verts.push_back(temp_vert);
            }
        }
    }

    // Sort temporary vertices by base name
    sort(temp_verts.begin(), temp_verts.end(), [](const ConstVertexPtr &a, const ConstVertexPtr &b) {
        return a->base_name() < b->base_name();
    });
    return temp_verts;
}


ostream &Linkage::write_dot(ostream &os, size_t &term_id, size_t &dummy_count, const string &color) const {

    // Increment term_id and dummy_count for unique identification
    ++term_id;
    ++dummy_count;

    string padding = "                ";
    vector<string> node_names, int_edge_names, ext_edge_names, null_nodes;

    // Define styles for nodes and edges
    string node_style = "color=\"" + color + "\", fontsize=20, style=bold";
    string null_node_style = "style=invis, shape=none, height=0.01,width=0.01";
    string ext_edge_style = "color=\"" + color + "\", style=bold, arrowsize=1.25";
    string int_edge_style = "color=\"" + color + "\", concentrate=false";

    size_t group_count = 0, temp_count = 0;
    bool began_temp = false;

    // Get sorted vertices and temporary vertices
    vector<ConstVertexPtr> vertices = sorted_vertices(as_link(shared_from_this()));
    vector<ConstVertexPtr> temp_verts = sorted_temp_vertices(as_link(shared_from_this()));

    // Iterate through each vertex
    for (size_t i = 0; i < vertices.size(); ++i) {
        const auto &current = vertices[i];
        bool in_temp = find(temp_verts.begin(), temp_verts.end(), current) != temp_verts.end();

        // Handle temporary vertices grouping
        if (in_temp && !began_temp) {
            node_names.push_back("subgraph cluster_tmp" + to_string(temp_count++) + "_" + to_string(term_id) + "{\n");
            began_temp = true;
        } else if (!in_temp && began_temp) {
            node_names.push_back("label=\"\";\nstyle=dashed;\nrank=min;\nclusterrank=global\n}\n");
            began_temp = false;
        }

        string l_id = to_string(i) + to_string(term_id);
        string current_node = current->base_name() + "_" + l_id;

        // Create node signature for non-empty base names
        if (!current->base_name().empty()) {
            string node_signature = current_node + " [label=\"" + current->base_name() + "\", " + node_style + ", group=" + to_string(group_count++) + "];\n";
            node_names.push_back(node_signature);
            append_edges(vertices, current, i, int_edge_names, l_id, term_id, int_edge_style);  // Append edges for the current node
        }
    }

    // Close temporary subgraph if it was opened
    if (began_temp) node_names.push_back("label=\"\";\nstyle=dashed;\nrank=min;\n}\n");

    // Append null nodes for vertices
    append_null_nodes(as_link(shared_from_this()), vertices, dummy_count, term_id, null_nodes, ext_edge_names, group_count, ext_edge_style, null_node_style);

    // Write all collected node and edge names to the output stream
    for (const auto &name : node_names) os << padding << name;
    for (const auto &edge : int_edge_names) os << padding << edge;
    for (const auto &edge : ext_edge_names) os << padding << edge;
    for (const auto &node : null_nodes) os << padding << node;

    return os;
}