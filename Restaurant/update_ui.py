import os
import re

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the new options block
    new_options = """<div class="options">
                  <h6>
                    ${{j.Price}}
                  </h6>
                  <div>
                    <a href="{% url 'add_to_cart' j.id %}" class="btn btn-warning btn-sm text-white mr-2" title="Add to Cart">
                        <i class="fa fa-shopping-cart"></i>
                    </a>
                     {% if request.user.is_authenticated %}
                        <a href="{% url 'toggle_wishlist' j.id %}" class="btn btn-danger btn-sm text-white" title="Wishlist">
                            <i class="fa fa-heart"></i>
                        </a>
                     {% endif %}
                  </div>
                </div>"""

    # Regex to capture the old options block
    # It starts with <div class="options">
    # Contains <h6>...{{j.Price}}...</h6>
    # Contains <a ... <svg ... </svg> ... </a>
    # Ends with </div>
    # handling multiline with re.DOTALL
    
    # Pattern explanation:
    # <div class="options">\s*                  -> Start of div
    # <h6>\s*{{j.Price}}\s*</h6>\s*             -> Price (menu.html has simple {{j.Price}}, home.html has it too)
    # <a.*?>\s*                                 -> Link start
    # <svg.*?</svg>\s*                          -> SVG block (non-greedy)
    # </a>\s*                                   -> Link end
    # </div>                                    -> Div end
    
    # However, home.html might have href="" vs menu.html href="{% url... %}"
    # So we match <a.*?> to be generic.
    
    pattern = r'<div class="options">\s*<h6>\s*{{j.Price}}\s*</h6>\s*<a.*?>\s*<svg.*?</svg>\s*</a>\s*</div>'
    
    new_content, count = re.subn(pattern, new_options, content, flags=re.DOTALL)
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath}: Replaced {count} occurrences.")
    else:
        print(f"No matches found in {filepath}")

    # Also update the box class if not already done
    # We want <div class="box"> -> <div class="box food-card"> but only inside the loop?
    # This might be risky with regex to context.
    # But we can try to replace <div class="box"> with <div class="box food-card"> 
    # BUT we need to be careful not to replace it everywhere.
    # The loop items are distinguishable because they are inside <div class="col... all {{j.Category}}">
    
    # Let's try to just fix the box class where it is followed by <div> <div class="img-box">
    
    box_pattern = r'(<div class="col-sm-6 col-lg-4 all {{j.Category}}">\s*)<div class="box">(\s*<div>\s*<div class="img-box">)'
    new_box_content = r'\1<div class="box food-card">\2'
    
    new_content_2, count_2 = re.subn(box_pattern, new_box_content, new_content if count > 0 else content, flags=re.DOTALL)
    
    if count_2 > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content_2)
        print(f"Updated {filepath}: Added food-card class to {count_2} items.")

base_dir = r"c:\Users\saron\django\Restaurent\Restaurant\Template"
update_file(os.path.join(base_dir, "home.html"))
update_file(os.path.join(base_dir, "menu.html"))
