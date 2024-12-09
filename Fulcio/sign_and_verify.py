from sigstore.sign import SigningContext
from sigstore.oidc import IdentityToken, detect_credential
from sigstore.models import Bundle
from securesystemslib.signer._utils import compute_default_keyid

# Step 1: Import necessary modules (this will auto-detect ambient credentials)
from sigstore.verify import Verifier


def sign_data(payload: bytes):
    """Signs data using ambient credentials."""

    try:
        # Step 2: Create a SigningContext with ambient authentication
        context = SigningContext.production()

        # Step 3: Use the signer (auto-detects credentials)
        with context.signer() as sigstore_signer:
            # Step 4: Sign the artifact (the payload)
            bundle = sigstore_signer.sign_artifact(payload)

        # Step 5: Return the signature bundle (serialized)
        bundle_json = bundle.to_json()
        return bundle_json

    except Exception as e:
        print(f"Error signing data: {e}")
        return None


def verify_signature(signature_bundle: dict, data: bytes):
    """Verify a signature using Sigstore's ambient credentials."""
    try:
        # Step 1: Load the signature bundle (normally returned from sign_data)
        bundle = Bundle.from_json(signature_bundle)

        # Step 2: Create a verifier to check the signature
        verifier = Verifier.production()

        # Step 3: Verify the artifact's signature
        verifier.verify_artifact(data, bundle)
        print("Signature verified successfully!")

    except Exception as e:
        print(f"Error verifying signature: {e}")


# Example usage
if __name__ == "__main__":
    # Data to be signed
    payload = b"Hello, this is the data to sign"

    # Sign the payload using Sigstore's ambient authentication
    signature_bundle = sign_data(payload)

    if signature_bundle:
        print("Data signed successfully!")

        # Verify the signature (for demonstration)
        verify_signature(signature_bundle, payload)
