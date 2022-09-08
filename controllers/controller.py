from pathlib import Path
from tkinter import Listbox, messagebox, ttk
from models.binary_file import BinaryFile
from models.callname import Callname
from models.config import Config
from models.model import Model
from views.view import View
import yaml

class Controller():
    def __init__(self):
        self.my_config = Config()
        self.model = Model()
        self.view = View(self)
        self.executable = BinaryFile("")
        self.over = BinaryFile("")
        self.callnames = BinaryFile("")
        self._load_settings()
        self.leagues_max_len = 61
        self.teams = []
        self.nationalities = []
        self.stadiums_list = []
        self.leagues_names_list = []
        self.callnames_list = []
        
        self.view.teamnames_tab.teamnames_list_box.bind(
            '<<ListboxSelect>>', 
            lambda event: self.tn_nt_data_to_entry(
                self.view.teamnames_tab.teamnames_list_box, 
                self.view.teamnames_tab.teamnames_box,
                self.view.teamnames_tab.teamnames_abb_box,
                self.view.teamnames_tab.teamnames_id_box,
                [] if self.teams ==[] else [team.full_name for team in self.teams],
                [] if self.teams ==[] else [team.abb_name for team in self.teams],
            )
        )
        
        self.view.nationalities_tab.nationalities_list_box.bind(
            '<<ListboxSelect>>', 
            lambda event: self.tn_nt_data_to_entry(
                self.view.nationalities_tab.nationalities_list_box, 
                self.view.nationalities_tab.nationalities_box,
                self.view.nationalities_tab.nationalities_abb_box,
                self.view.nationalities_tab.nationalities_id_box,
                [] if self.nationalities ==[] else [nationality.full_name for nationality in self.nationalities],
                [] if self.nationalities ==[] else [nationality.abb_name for nationality in self.nationalities],
            )
        )

        self.view.stadiums_tab.stadiums_list_box.bind(
            '<<ListboxSelect>>', 
            lambda event: self.st_lg_data_to_entry(
                self.view.stadiums_tab.stadiums_list_box, 
                self.view.stadiums_tab.stadiums_box,
                self.view.stadiums_tab.stadiums_id_box,
                self.stadiums_list,
            )
        )

        self.view.leagues_tab.league_list_box.bind(
            '<<ListboxSelect>>', 
            lambda event: self.st_lg_data_to_entry(
                self.view.leagues_tab.league_list_box, 
                self.view.leagues_tab.league_box,
                self.view.leagues_tab.league_id_box,
                self.leagues_names_list,
            )
        )

        self.view.callnames_tab.callnames_list_box.bind(
            '<<ListboxSelect>>', 
            lambda event: self.callnames_data_to_entry(
                self.view.callnames_tab.callnames_list_box, 
                self.view.callnames_tab.callnames_box,
                self.view.callnames_tab.callnames_id_box,
                self.view.callnames_tab.callnames_file_id_box,
                self.view.callnames_tab.callnames_afs_id_cbox,
                [] if self.callnames_list ==[] else self.callnames_list,
            )
        )

    def _load_settings(self):
        load_defaults = False
        try:
            with open(str(Path().absolute()) + "/settings.yaml") as stream:
                self.settings_file = yaml.safe_load(stream)
                self._load_config(self.my_config.filelist.index(self.settings_file.get('Last Config File Used')))
        except Exception as e:
            load_defaults = True
            messagebox.showinfo(title=self.view.appname, message=f"No setting file found\nLoading first config file")
        if load_defaults:
            try:
                self._load_config(0)
            except Exception as e:
                messagebox.showerror(title=self.view.appname, message=f"No config files found code error {e}")
                self.view.destroy()

    def save_settings_and_close(self):
        settings_file_name = str(Path().absolute()) + "/settings.yaml"
        
        dict_file = {
            'Last Config File Used' : self.my_config.file_location,
        }

        settings_file = open(settings_file_name, "w")
        yaml.dump(dict_file, settings_file)
        settings_file.close()
        self.view.destroy()


    def _load_config(self, idx):
        self.my_config.load_config(idx)
        self.view.appname = "PES/WE/JL Text Editor " + self.my_config.file["Gui"]["Game Name"]
        self.view.title(self.view.appname)
        # Game data
        self.base_address = self.my_config.file["Game Data"]["Base Address"]
        self.total_stadiums = self.my_config.file["Game Data"]["Total Stadiums"]
        self.stadiums_max_len = self.my_config.file["Game Data"]["Stadium Name Lenght"]
        self.total_leagues = self.my_config.file["Game Data"]["Total Leagues"]
        self.total_teams = self.my_config.file["Game Data"]["Total Teams"]
        

        # SLXX offsets

        self.names_offsets_table = self.my_config.file["SLXX Offsets"]["Teams Offsets Table"]
        self.names_data_size = self.my_config.file["SLXX Offsets"]["Teams Table Size"]
        self.teams_names_text_size = self.my_config.file["SLXX Offsets"]["Teams Text Data Size"]
        self.nationalities_offsets_table = self.my_config.file["SLXX Offsets"]["Nationalities Offsets Table"]
        self.nt_data_size = self.my_config.file["SLXX Offsets"]["Nationalities Table Size"]


        # over offsets
        self.stadiums_offsets_table = self.my_config.file["OVER Offsets"]["Stadiums Offsets Table 1"]
        self.stadiums_offsets_table2 = self.my_config.file["OVER Offsets"]["Stadiums Offsets Table 2"]
        self.leagues_offsets_table = self.my_config.file["OVER Offsets"]["Leagues Offsets Table 1"]
        self.leagues_offsets_table2 = self.my_config.file["OVER Offsets"]["Leagues Offsets Table 2"]

        # callname
        self.callname_len = self.my_config.file["Callnames"]["Name Lenght"]
        self.callname_encoding = self.my_config.file["Callnames"]["Encoding"]

    def main(self):
        self.view.main()

    def on_open_file_menu_click(self):
        file_path = (self.model.open_file())
        if file_path != "":
            self.executable.filename = file_path
        if (
            self.executable.size > 0 and 
            self.names_offsets_table != 0 and 
            self.nationalities_offsets_table != 0
        ):
            # loading teamnames into listbox
            self.names_start_offset = self.model.get_name_offset(self.executable.file_bytes, self.names_offsets_table)  - self.base_address

            self.teams = self.model.get_teams(self.executable.file_bytes, self.names_offsets_table, self.total_teams, self.base_address)
            
            self.view.teamnames_tab.teamnames_list_box.delete(0, "end")
            self.view.teamnames_tab.teamnames_list_box.insert("end", *[team.full_name for team in self.teams])
            
            # loading nationalities into listbox
            self.total_nationalities = int(self.nt_data_size/8)
            self.nationalities_start_offset = self.model.get_name_offset(self.executable.file_bytes, self.nationalities_offsets_table) - self.base_address
            self.nationalities_text_size = self.nationalities_offsets_table - (self.nationalities_start_offset)
            self.nationalities = self.model.get_nationalities(self.executable.file_bytes, self.nationalities_offsets_table, self.total_nationalities, self.base_address)

            self.view.nationalities_tab.nationalities_list_box.delete(0, "end")
            self.view.nationalities_tab.nationalities_list_box.insert("end", *[nationality.full_name for nationality in self.nationalities])
            self.view.file_menu.entryconfig("Save SLXX", state='normal')


    def on_open_over_menu_click(self):
        file_path = (self.model.open_file())
        if file_path != "":
            self.over.filename = file_path
        if (
            self.over.size > 0 and 
            self.stadiums_offsets_table != 0 and 
            self.stadiums_offsets_table2 != 0 and 
            self.leagues_offsets_table != 0 and 
            self.leagues_offsets_table2 != 0
        ):
            # loading stadiums into listbox
            
            self.stadiums_list = self.model.get_stadiums_names(self.over.file_bytes, self.stadiums_offsets_table, self.total_stadiums, self.stadiums_max_len)
            
            self.view.stadiums_tab.stadiums_list_box.delete(0, "end")
            self.view.stadiums_tab.stadiums_list_box.insert("end", *self.stadiums_list)
            
            # loading leagues into listbox
            
            self.leagues_names_list = self.model.get_leagues_names(self.over.file_bytes, self.leagues_offsets_table, self.total_leagues, self.leagues_max_len)
            
            self.view.leagues_tab.league_list_box.delete(0, "end")
            self.view.leagues_tab.league_list_box.insert("end", *self.leagues_names_list)
            self.view.file_menu.entryconfig("Save OVER", state='normal')

    def on_open_callname_file_menu_click(self):
        file_path = (self.model.open_file())
        if file_path != "":
            self.callnames.filename = file_path
        if (
            self.callnames.size > 0 and 
            self.callname_len != 0
        ):
            # loading teamnames into listbox
            self.callnames_list = self.model.get_callnames(
                self.callnames.file_bytes, 
                self.callname_len,
                self.callname_encoding,
            )
            
            self.view.callnames_tab.callnames_list_box.delete(0, "end")
            self.view.callnames_tab.callnames_list_box.insert("end", *[callname.name for callname in self.callnames_list])
            
            self.view.file_menu.entryconfig("Save Callname File", state='normal')


    def tn_nt_data_to_entry(self, listbox: Listbox, full_name: ttk.Entry, abb: ttk.Entry, id_entry: ttk.Entry, fullnames_list:list, short_names_list: list):
        if listbox.curselection() == ():
            return 0

        idx = listbox.curselection()[0]
        
        full_name.delete(0,'end')
        full_name.insert(0, fullnames_list[idx])
        
        abb.delete(0,'end')
        abb.insert(0, short_names_list[idx])
        
        id_entry.configure(state='normal')
        id_entry.delete(0,'end')
        id_entry.insert(0, idx)
        id_entry.configure(state='readonly')

    def st_lg_data_to_entry(self, listbox: Listbox, full_name: ttk.Entry, id_entry: ttk.Entry, fullnames_list:list):
        if listbox.curselection() == ():
            return 0
        idx = listbox.curselection()[0]
        
        full_name.delete(0,'end')
        full_name.insert(0, fullnames_list[idx])
                
        id_entry.configure(state='normal')
        id_entry.delete(0,'end')
        id_entry.insert(0, idx)
        id_entry.configure(state='readonly')

    def callnames_data_to_entry(
        self, 
        listbox: Listbox, 
        callnames_box: ttk.Entry, 
        id_entry: ttk.Entry, 
        file_id_box: ttk.Entry, 
        afs_id_cbox: ttk.Combobox, 
        callnames:"list[Callname]",
    ):
        if listbox.curselection() == ():
            return 0
        idx = listbox.curselection()[0]
        id_entry.configure(state='normal')
        id_entry.delete(0,'end')
        id_entry.insert(0, callnames[idx].idx)
        id_entry.configure(state='readonly')
        callnames_box.delete(0,'end')
        callnames_box.insert(0, callnames[idx].name)
        file_id_box.delete(0,'end')
        file_id_box.insert(0, callnames[idx].file_1_id)
        afs_id_cbox.current(callnames[idx].afs_1_id)


    def teams_apply_btn_action(self, idx: int, name:str, abb:str):
        self.teams[idx].full_name = name
        self.teams[idx].abb_name = abb
        self.view.teamnames_tab.teamnames_list_box.delete(idx,idx)
        self.view.teamnames_tab.teamnames_list_box.insert(idx, self.teams[idx].full_name)
        self.view.teamnames_tab.teamnames_list_box.select_set(idx)

    def nationality_apply_btn_action(self, idx: int, name:str, abb:str):
        self.nationalities[idx].full_name = name
        self.nationalities[idx].abb_name = abb
        self.view.nationalities_tab.nationalities_list_box.delete(idx,idx)
        self.view.nationalities_tab.nationalities_list_box.insert(idx, self.nationalities[idx].full_name)
        self.view.nationalities_tab.nationalities_list_box.select_set(idx)

    def stadiums_apply_btn_action(self, idx: int, name:str):
        if len(name)>= self.stadiums_max_len:
            messagebox.showerror(title = self.view.appname, message = f"Stadium name can be only {self.stadiums_max_len - 1} long")
            return 0
        self.stadiums_list[idx] = name
        self.view.stadiums_tab.stadiums_list_box.delete(idx,idx)
        self.view.stadiums_tab.stadiums_list_box.insert(idx, self.stadiums_list[idx])
        self.view.stadiums_tab.stadiums_list_box.select_set(idx)

    def leagues_apply_btn_action(self, idx: int, name:str):
        if len(name)>= self.leagues_max_len:
            messagebox.showerror(title = self.view.appname, message = f"League name can be only {self.leagues_max_len - 1} long")
            return 0
        self.leagues_names_list[idx] = name
        self.view.leagues_tab.league_list_box.delete(idx,idx)
        self.view.leagues_tab.league_list_box.insert(idx, self.leagues_names_list[idx])
        self.view.leagues_tab.league_list_box.select_set(idx)

    def callnames_apply_btn_action(self, idx: int, name:str, file_id:int, afs_id:int):
        if len(name)>self.callname_len:
            messagebox.showerror(title = self.view.appname, message = f"Callname name can be only {self.callname_len -1} long")
            return 0
        self.callnames_list[idx].name = name
        self.callnames_list[idx].file_1_id = file_id
        self.callnames_list[idx].file_2_id = file_id
        self.callnames_list[idx].afs_1_id = afs_id
        self.callnames_list[idx].afs_2_id = afs_id

        self.view.callnames_tab.callnames_list_box.delete(idx,idx)
        self.view.callnames_tab.callnames_list_box.insert(idx, self.callnames_list[idx].name)
        self.view.callnames_tab.callnames_list_box.select_set(idx)


    def on_click_on_save_SLXX(self):
        try:
            self.model.write_team_names(self.teams, self.base_address, self.names_start_offset ,self.names_offsets_table, self.teams_names_text_size, self.executable)
            self.model.write_nt(self.nationalities, self.base_address, self.nationalities_start_offset ,self.nationalities_offsets_table, self.nationalities_text_size, self.executable)
            messagebox.showinfo(title = self.view.appname, message = f"All changes saved at {self.executable.filename}")
        except Exception as e:
            messagebox.showinfo(title = self.view.appname, message = f"Error while saving, error type: {e}")

    def on_click_on_save_OVER(self):
        try:
            self.model.write_stadiums_names(self.stadiums_list, self.stadiums_offsets_table,self.stadiums_max_len, self.over)
            self.model.write_stadiums_names(self.stadiums_list, self.stadiums_offsets_table2,self.stadiums_max_len, self.over)
            self.model.write_leagues_names(self.leagues_names_list, self.leagues_offsets_table,self.leagues_max_len, self.over)
            self.model.write_leagues_names(self.leagues_names_list, self.leagues_offsets_table2,self.leagues_max_len, self.over)
            messagebox.showinfo(title = self.view.appname, message = f"All changes saved at {self.over.filename}")
        except Exception as e:
            messagebox.showinfo(title = self.view.appname, message = f"Error while saving, error type: {e}")

    def on_click_on_save_callname(self):
        try:
            self.model.write_callnames(self.callnames_list, self.callname_len, self.callnames)
            messagebox.showinfo(title = self.view.appname, message = f"All changes saved at {self.callnames.filename}")
        except Exception as e:
            messagebox.showinfo(title = self.view.appname, message = f"Error while saving, error type: {e}")
        

if __name__ == "__main__":
    text_editor = Controller()
    text_editor.main()
