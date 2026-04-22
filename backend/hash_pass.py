import bcrypt

password = "Congty@123".encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())

print("-" * 50)
print(f"Mã băm mới để dán vào Supabase:\n{hashed.decode('utf-8')}")
print("-" * 50)