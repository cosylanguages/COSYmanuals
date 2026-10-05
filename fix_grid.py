for lvl in ['a1', 'a2', 'b1', 'b2', 'c1', 'c2']:
    idx_path = f"manuals/fr/grammar/{lvl}/index.html"
    with open(idx_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Check if there are part-cards after the parts-grid div closes
    if '<div class="parts-grid">' in content:
        # Move all appended part-cards inside <div class="parts-grid"> ... </div>
        # Split at </main>
        parts = content.split('</main>')
        main_body = parts[0]
        rest = '</main>' + parts[1]

        # Find position of last </div> in main_body
        last_div_pos = main_body.rfind('</div>')
        if last_div_pos != -1:
            # Shift the extra cards inside the parts-grid container before that last </div>
            # Extract cards appended at end of main_body
            # Find where parts-grid starts
            grid_pos = main_body.find('<div class="parts-grid">')
            # The cards that were added after grid_pos
            # Let's clean up and reconstruct cleanly
            pass
