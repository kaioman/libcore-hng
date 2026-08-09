from custom_app_init.custom_app_init_enc import config

class TestSetupConfiguration:

    def test_reference_config_value(self):
        assert config.logging.log_rotation_when == "midnight"
        assert config.test1.dammy_key == "xxx-xxx-yyy-zzzz"
        assert config.test1.append_member == "add Member override"
        assert config.test1.dammy_key1 == "AA-111^xxxxx"
        assert config.test1.dammy_key2 == "BB-111^xxxxx"
        assert config.test1.dammy_key3 == "CC-111^xxxxx"
        assert config.test2.dammy_key1 == "AA-211^xxxxx"
        assert config.test2.dammy_key2 == "BB-211^xxxxx"
        assert config.test2.dammy_key3 == "CC-211^xxxxx"