# import ipfshttpclient
# from web3 import Web3
# import json
# import os
# from fastapi import FastAPI, UploadFile, File
# from fastapi.middleware.cors import CORSMiddleware
# import uvicorn

# # Initialize FastAPI app
# app = FastAPI()

# # CORS configuration for React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all origins; adjust for production if needed
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # IPFS and blockchain configuration
# INFURA_URL = 'https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID'
# PRIVATE_KEY = 'YOUR_PRIVATE_KEY'
# CONTRACT_ADDRESS = '0x0eb4b3b319479d739f24dfe7ea323ec09a642a0b'
# CONTRACT_ABI = json.loads('[...]')  # Replace with the actual ABI

# # Ethereum connection
# web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# # Connect to IPFS
# def upload_to_ipfs(file_path):
#     try:
#         client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001/http')
#         res = client.add(file_path)
#         return res['Hash']
#     except Exception as e:
#         print("Error connecting to IPFS:", e)
#         return None

# # Store IPFS hash on blockchain
# def store_ipfs_hash_on_blockchain(patient_id, ipfs_hash):
#     try:
#         account = web3.eth.account.from_key(PRIVATE_KEY)
#         contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

#         nonce = web3.eth.get_transaction_count(account.address)
#         tx = contract.functions.uploadFile(patient_id, ipfs_hash).build_transaction({
#             'from': account.address,
#             'nonce': nonce,
#             'gas': 2000000,
#             'gasPrice': web3.to_wei('20', 'gwei')
#         })

#         signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
#         tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
#         return web3.to_hex(tx_hash)
#     except Exception as e:
#         print("Blockchain transaction error:", e)
#         return None

# # Main function to be called directly
# def main(patient_id, file_path):
#     try:
#         # Upload file to IPFS
#         ipfs_hash = upload_to_ipfs(file_path)

#         if not ipfs_hash:
#             print("Failed to upload file to IPFS")
#             return

#         # Store hash on the blockchain
#         tx_hash = store_ipfs_hash_on_blockchain(patient_id, ipfs_hash)
#         if not tx_hash:
#             print("Failed to store IPFS hash on the blockchain")
#             return

#         print(f"File uploaded successfully!")
#         print(f"IPFS URL: https://ipfs.io/ipfs/{ipfs_hash}")
#         print(f"Ethereum Transaction Hash: {tx_hash}")
#     except Exception as e:
#         print("Error in main function:", e)

# # API endpoint for uploading a file via FastAPI
# @app.post("/upload")
# async def upload_file(patient_id: int, file: UploadFile = File(...)):
#     try:
#         # Save file locally
#         file_path = f"/tmp/{file.filename}"
#         with open(file_path, "wb") as f:
#             f.write(await file.read())

#         # Upload file to IPFS
#         ipfs_hash = upload_to_ipfs(file_path)
#         os.remove(file_path)  # Clean up the temporary file

#         if not ipfs_hash:
#             return {"error": "Failed to upload file to IPFS"}

#         # Store hash on the blockchain
#         tx_hash = store_ipfs_hash_on_blockchain(patient_id, ipfs_hash)
#         if not tx_hash:
#             return {"error": "Failed to store IPFS hash on the blockchain"}

#         return {
#             "ipfs_hash": ipfs_hash,
#             "transaction_hash": tx_hash
#         }
#     except Exception as e:
#         print("Error:", e)
#         return {"error": "Failed to upload file"}

# # Run FastAPI app if this file is executed as a script
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 2:
#         patient_id = int(sys.argv[1])
#         file_path = sys.argv[2]
#         main(patient_id, file_path)
#     else:
#         print("Running as FastAPI server...")
#         uvicorn.run(app, host="0.0.0.0", port=8000)
