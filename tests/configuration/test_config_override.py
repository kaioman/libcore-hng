from custom_app_init.custom_app_init_override import config

class TestSetupConfiguration:

    def test_reference_config_value(self):
        assert config.logging.ext1 == "ext1_value"
        assert config.logging.log_rotation_when == "midnight"