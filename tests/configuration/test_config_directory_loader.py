from custom_app_init.custom_app_init_enc import config

class TestSetupConfiguration:

    def test_reference_config_value(self):
        assert config.test1.dammy_key == "xxx-xxx-yyy-zzzz"
