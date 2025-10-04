import io
import pyotp
import base64
import qrcode
from app.config.settings import settings
from app.schema.totp import SeedURIImage,SeedFullInfo

class TOTPHelper():

    @staticmethod
    def generate_seed():
        """Generate a random base32 secret key for TOTP."""

        # Generate a random base32 secret key for TOTP
        return pyotp.random_base32()

    @staticmethod
    def generate_seed_uri(seed:str,name:str)->str:
        """Generate a seed URI for the given seed and name.
        Args:
            seed (str): The TOTP secret seed.
            name (str): The name of the user or account.
        Returns:
            str: The provisioning URI for the TOTP.
        """
        # Get Issuer name from settings
        totp=pyotp.TOTP(seed)
        # Generate the provisioning URI for the TOTP
        return totp.provisioning_uri(name=name,issuer_name=settings.issuer_name)

    
    @staticmethod
    def verify_totp(seed:str,totp_code:str)->bool:
        """Verify the provided TOTP code against the seed.

        Args:
            seed (str): The TOTP secret seed.
            totp_code (str): The TOTP code to verify.

        Returns:
            bool: True if the TOTP code is valid, False otherwise.
        """
        # Verify the provided TOTP code against the seed
        totp=pyotp.TOTP(seed)
        # Check if the provided TOTP code is valid
        return totp.now()==totp_code
    
    @staticmethod
    def generate_seed_uri_image(seed:str,username:str)->SeedURIImage:
        """Generate a seed URI and a QR code image for the given seed and name.

        Args:
            seed (str): The TOTP secret seed.
            username (str): The username of the user or account.

        Returns:
            SeedURIImage: An object containing the seed URI and the QR code image.
        """
        #Generate seed uri
        seed_uri=TOTPHelper.generate_seed_uri(seed,username)
        # Create a QR code image from the seed URI
        img = qrcode.make(data=seed_uri)
        # Prepare a bytes buffer to hold the image data
        img_byte_arr = io.BytesIO()
        # Save the QR code image to the buffer in PNG format
        img.save(img_byte_arr, format='PNG')
        # Move the buffer's cursor to the beginning
        img_byte_arr.seek(0)
        # Return the seed URI and the QR code image encoded as a base64 string
        return SeedURIImage(seed_uri=seed_uri, qrcode=base64.b64encode(img_byte_arr.read()).decode())
    
    @staticmethod
    def generate_seed_with_uri_image(username:str)->SeedFullInfo:
        """Generate a random base32 secret key, a seed URI, and a QR code image for the given name.

        Args:
            username (str): The username of the user or account.

        Returns:
            SeedFullInfo: An object containing the seed URI and the QR code image.
        """
        # Generate a random base32 secret key
        seed = TOTPHelper.generate_seed()
        # Generate the seed URI and QR code image
        totp_info= TOTPHelper.generate_seed_uri_image(seed, username)
        return SeedFullInfo(seed=seed,user_name=username,seed_uri=totp_info.seed_uri,qrcode=totp_info.qrcode)
    
    @staticmethod
    def encrypt_seed(seed:str)->str:
        """
        Encrypt the TOTP seed using Base64 encoding.
        Args:
            seed (str): The TOTP secret seed.
        Returns:
            str: The Base64 encoded string of the seed.
        """
        # Encode the Base64 string to bytes
        base64_bytes = seed.encode('utf-8')
        # Perform Base64 encoding
        encoded_bytes = base64.b64encode(base64_bytes)
        # Return econding string by decoding the bytes
        return encoded_bytes.decode('utf-8')

    @staticmethod
    def decrypt_seed(encryped_seed:str)->str:
        """
        Decrypt the TOTP seed using Base64 decoding.
        Args:
            encryped_seed (str): The Base64 encoded string of the seed.
        Returns:
            str: The TOTP secret seed.
        """
        # Encode the Base64 string to bytes
        base64_bytes = encryped_seed.encode('utf-8')
        # Perform Base64 decoding
        decoded_bytes = base64.b64decode(base64_bytes)
        # Return orginal string by decoding the bytes
        return decoded_bytes.decode('utf-8')
