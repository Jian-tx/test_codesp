import numpy as np

file_path = "/workspaces/test_codesp/llm-universe/data_base/vector_db/7d8ba171-c889-4e40-ae42-f349b34c2a5b/data_level0.bin"

# 读取 float32 数据
embeddings = np.fromfile(file_path, dtype=np.float32)

total_size = embeddings.size
print(f"总元素数: {total_size}")

# 自动找出所有可能的维度（1~2048）
print("\n可行的向量维度（总元素数可被整除）：")
possible_dims = []
for dim in range(1, 2049):
    if total_size % dim == 0:
        num_vectors = total_size // dim
        if 2 <= num_vectors <= 50000:  # 限制向量个数范围（避免极端情况）
            possible_dims.append((dim, num_vectors))

for dim, count in possible_dims:
    print(f"维度: {dim}, 向量数: {count}")

# 如果你希望试其中一个，比如 dim = 1571：
chosen_dim = possible_dims[-1][0]  # 例如选最后一个候选维度
embeddings = embeddings.reshape((-1, chosen_dim))
print(f"\n重塑后的 shape: {embeddings.shape}")
print(f"第一个向量:\n{embeddings[0]}")
