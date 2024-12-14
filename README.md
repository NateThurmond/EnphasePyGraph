## Initial

python3 -m venv venv

## Everytime

source venv/bin/activate
pip install -r requirements.txt

## In pyenv

deactivate

## Useful during dev after adding new packages

pip freeze > requirements.txt

Inspiration, code snippets, etc.

-   [Enphase local IQ Gateway API Documentation](https://enphase.com/download/accessing-iq-gateway-local-apis-or-local-ui-token-based-authentication?srsltid=AfmBOoomOm3FlVi2W7OwHoV-aJ-OdVSL5kJrt5HmSgAqJBBv4qaDluRW)
-   [Enphase IVP PDM Route troubleshooting](https://support.enphase.com/s/question/0D53m00009Ph9G0CAJ/why-am-i-still-unable-to-pull-daily-weekly-and-lifetime-production-data-from-local-api-with-homeowner-token)
