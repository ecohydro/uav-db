# %%
with open(r"../image_lists/all_tif_images.txt", 'r') as fp:
    num_lines = sum(1 for line in fp)
    print('Total lines:', num_lines)

# %%
