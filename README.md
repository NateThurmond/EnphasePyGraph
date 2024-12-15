# Enphase Python Graph

Queries local Enphase IQ Gateway API data to build out metrics for graph data

## Description

The Enphase App (and site) rely on data uploaded from your local Enphase IQ Gateway into the cloud. I often notice significant delays in reporting within the app resulting directly from this data not being uploaded. I wanted a way to report on live data direct from my system w/o having the extra dependencies of live internet connection or enphase application service outagages

<img src="assets/images/enphasePyApp.png" width="450" />

### Dependencies

-   Python3
-   Local Enphase IQ Gateway
-   pyenv (optional, for managing Python versions and virtual environments)

### Setup

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/pyEnphaseGraph.git
    cd pyEnphaseGraph
    ```
2. **Set up the virtual environment (optional, if using pyenv)**:
    ```pyenv virtualenv 3.10.0 myenv
    pyenv activate myenv
    ```
3. **Install the dependencies**:  
   pip install -r requirements.txt

4. **Create a .env file with the necessary environment variables**:  
    E.G.  
   ENPHASE_IQ_GATEWAY_IP=http://your-enphase-iq-gateway-ip

5. **Run the script:**
    ```
    python queryEnphaseGateway.py
    ```

Inspiration, code snippets, etc.

-   [Enphase local IQ Gateway API Documentation](https://enphase.com/download/accessing-iq-gateway-local-apis-or-local-ui-token-based-authentication?srsltid=AfmBOoomOm3FlVi2W7OwHoV-aJ-OdVSL5kJrt5HmSgAqJBBv4qaDluRW)
-   [Enphase IVP PDM Route troubleshooting](https://support.enphase.com/s/question/0D53m00009Ph9G0CAJ/why-am-i-still-unable-to-pull-daily-weekly-and-lifetime-production-data-from-local-api-with-homeowner-token)
