from auxiliary_for_tests import *
import flask_testing
from database_setup import test_database_create
from sources import app, db
from pony.orm import db_session, select
import time


class RetrosynthesisTestCase(flask_testing.LiveServerTestCase, flask_testing.TestCase):
    """
    Tests retrosynthesis works.
    """

    def create_app(self):
        app.config.from_object('config.TestConfig')
        test_database_create(db)
        return app

    def setUp(self):
        setup_selenium(self)

    def tearDown(self):
        self.driver.quit()
        restore_db()

    def click_node(self):
        # click on node in cytoscape
        elem = self.driver.find_element_by_id('retrosynthesis-cytoscape')
        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.move_to_element_with_offset(elem, 471, 271)
        action.click()
        action.perform()
        time.sleep(1)


    def reload_retrosynthesis(self):
        self.driver.find_element_by_id('saved-results-tab').click()
        time.sleep(1)
        buttons = self.driver.find_elements(By.CLASS_NAME, 'btn-primary')
        for button in buttons:
            if button.text == 'Reload':
                print("clicking reload button")
                scroll_element(self, 'saved-results-list')
                button.click()
                time.sleep(5)
                break

    def test_canvas_present(self):
        """Tests the retrosynthesis canvas appears"""
        login(self)
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        cytoscape = self.driver.find_element_by_id("retrosynthesis-cytoscape")
        self.assertNotEqual(None, cytoscape)

    def test_retrosynthesis_process_and_saving(self):
        """Tests the retrosynthesis works and puts the expected message above the cytoscape canvas
        Also, tests saving to database
        """
        login(self)
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        clear_and_send_keys(self, "smiles-input", "COc1ccc(OCCNC(=O)c2c(C)nc3cc(C)ccn23)cc1")
        time.sleep(1)
        # perform retrosynthesis - api must be active
        self.driver.find_element_by_id('btn-retrosynthesis').click()
        # wait up to 120 seconds (24 * 5) checking every 5 seconds if the process is complete
        for i in range(24):
            time.sleep(5)
            try:
                user_message = self.driver.find_element_by_id("user-message").text
                self.assertEqual("Interactive display for retrosynthesis of COc1ccc(OCCNC(=O)c2c(C)nc3cc(C)ccn23)cc1",
                                 user_message)
                break
            except:
                pass
        time.sleep(10)
        # save to database
        self.driver.find_element_by_id('open-save-modal').click()
        time.sleep(1)
        clear_and_send_keys(self, 'save-modal-name', 'new test retrosynthesis')
        self.driver.find_element_by_id('save-modal-save-button').click()
        time.sleep(1)
        save_message = self.driver.find_element_by_id('modal-save-message').text
        self.assertEqual("Retrosynthesis: new test retrosynthesis saved successfully",
                         save_message)
        # test that we cannot save a duplicate
        self.driver.find_element_by_id('save-modal-save-button').click()
        time.sleep(1)
        save_failed_message = self.driver.find_element_by_id('modal-save-message').text
        self.assertEqual("This route has already been saved with the name new test retrosynthesis",
                         save_failed_message)
        # confirm 1 item in database with matching name
        with db_session:
            saved_retrosynthesis = select(x for x in db.Retrosynthesis if x.name == 'new test retrosynthesis')[:]
        self.assertEqual(1, len(saved_retrosynthesis))

    def test_invalid_smiles(self):
        """Tests the smiles validation """
        login(self)
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        clear_and_send_keys(self, "smiles-input", "not a smiles string")
        time.sleep(2)
        self.driver.find_element_by_id('btn-retrosynthesis').click()
        time.sleep(2)
        user_message = self.driver.find_element_by_id("user-message").text
        self.assertEqual("Please enter a valid SMILES", user_message)

    def test_retrosynthesis_from_demo_sketcher_works(self):
        """Tests the sketcher exports the SMILES to the retrosynthesis page and input field from demo"""
        login(self)
        self.driver.find_element_by_id("TopNavSketcherButton").click()
        time.sleep(2)
        self.driver.find_element_by_id("demo-button").click()
        time.sleep(2)
        self.driver.find_element_by_id("retrosynthesis-export").click()
        time.sleep(2)
        exported_smiles = self.driver.find_element_by_id("smiles-input").get_attribute("value")
        self.assertEqual("CCNC(=O)C1=CC=CC=C1", exported_smiles)

    def test_retrosynthesis_from_experiment_sketcher_works(self):
        """Tests the sketcher exports the SMILES to the retrosynthesis page and input field from experiment"""
        login(self)
        select_workgroup(self)
        make_new_reaction(self, "reaction-1")
        time.sleep(5)
        scroll_to_bottom(self)
        time.sleep(1)
        self.driver.find_element_by_id("demo-button").click()  # refers to example reaction not demo mode
        time.sleep(2)
        self.driver.find_element_by_id("retrosynthesis-export").click()
        time.sleep(2)
        exported_smiles = self.driver.find_element_by_id("smiles-input").get_attribute("value")
        self.assertEqual("CCNC(=O)C1=CC=CC=C1", exported_smiles)

    def test_clicking_node(self):
        """Tests the reaction conditions table and compound table appear when clicking on a node"""
        login(self, "BB_Test", "BB_login")
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        self.reload_retrosynthesis()
        self.click_node()
        scroll_to_top(self)
        self.driver.find_element_by_id('compound-tab').click()
        # check conditions table appears
        conditions_data_table = self.driver.find_element_by_id('reaction-conditions-data-table')
        self.assertIsNotNone(conditions_data_table)
        compound_not_found_message = self.driver.find_element_by_id('compound-feedback').text
        self.assertEqual('Compound not in database', compound_not_found_message)

    def test_route_data_table(self):
        """Tests route data table appears when reloading"""
        login(self, "BB_Test", "BB_login")
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        self.reload_retrosynthesis()
        routes_table = self.driver.find_element_by_id('route-data-table')
        self.assertIsNotNone(routes_table)

    def test_route_sustainability_table(self):
        """Tests sustainability table appears when reloading"""
        login(self, "BB_Test", "BB_login")
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        self.reload_retrosynthesis()
        routes_table = self.driver.find_element_by_id('route-sustainability-table')
        self.assertIsNotNone(routes_table)

    def test_sliders(self):
        """Tests sliders appear"""
        login(self, "BB_Test", "BB_login")
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        self.reload_retrosynthesis()
        solvent_slider = self.driver.find_element_by_id('solvent-slider-div')
        self.assertIsNotNone(solvent_slider)

    def test_export_to_reaction(self):
        login(self, "BB_Test", "BB_login")
        self.driver.find_element_by_id("retrosynthesis").click()
        time.sleep(2)
        self.reload_retrosynthesis()
        self.click_node()
        scroll_to_top(self)
        self.driver.find_element_by_id('reaction-tab').click()
        scroll_to_bottom(self)
        self.driver.find_element_by_id('open-new-reaction-modal').click()
        clear_and_send_keys(self, 'new-reaction-name', 'retrosynthesis-test-reaction')
        self.driver.find_element_by_id('new-reaction-data-submit').click()
        time.sleep(8)
        # confirm sketcher
        smiles = sketcher_to_smiles(self)
        self.assertEqual('COc1ccc(OCCN)cc1.Cc1nc2cc(C)ccn2c1C(O)=O>>COc1ccc(OCCNC(=O)c2c(C)nc3cc(C)ccn23)cc1',
                         smiles)
        # confirm database
        with db_session:
            saved_reaction = select(x for x in db.Reaction if x.name == 'retrosynthesis-test-reaction')[:]
        self.assertEqual(1, len(saved_reaction))


