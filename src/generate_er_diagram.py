import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def generate_er_diagram():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DIAGRAMS_DIR = os.path.join(BASE_DIR, 'diagrams')
    os.makedirs(DIAGRAMS_DIR, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')
    
    tables = {
        "stores": (10, 80),
        "products": (40, 80),
        "customer_details": (70, 80),
        "store_sales_header": (40, 50),
        "store_sales_line_items": (40, 20),
        "loyalty_rules": (10, 20),
        "promotion_details": (70, 20),
    }
    
    # Draw boxes
    for table, (x, y) in tables.items():
        rect = patches.Rectangle((x, y), 20, 10, linewidth=1, edgecolor='black', facecolor='lightblue')
        ax.add_patch(rect)
        plt.text(x + 10, y + 5, table, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Draw simple lines mapping relationships (rough approximations)
    # Header -> Store
    plt.plot([50, 20], [50, 80], 'k-', lw=1, alpha=0.5) 
    # Header -> Customer
    plt.plot([50, 80], [50, 80], 'k-', lw=1, alpha=0.5)
    # LineItems -> Header
    plt.plot([50, 50], [20, 50], 'k-', lw=1, alpha=0.5)
    # LineItems -> Products
    plt.plot([50, 50], [20, 80], 'k-', lw=1, alpha=0.5)

    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    plt.title("Database ER Diagram", fontsize=14)
    
    output_path = os.path.join(DIAGRAMS_DIR, 'er_diagram.png')
    plt.savefig(output_path)
    plt.close()
    print("ER diagram generated in diagrams/")

if __name__ == "__main__":
    generate_er_diagram()
