import struct
from tkinter import filedialog

from models.callname import Callname
from .team import Team
from .nationality import Nationality
from .binary_file import BinaryFile

class Model():
    def __init__(self):
        return
    
    def open_file(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        filetypes = [
            #("PES/WE/JL PS2 Option File", ".psu .xps"),
            ('All files', '*.*'),
        ]

        filename = filedialog.askopenfilename(
            title=f'Select your game executable',
            initialdir='.',
            filetypes=filetypes)
        return filename        

    def get_name_offset(self, file_bytes: bytes, offset: int):
        return struct.unpack("<I",file_bytes[offset : offset + 4])[0]


    def get_teams(self, file_bytes: bytes, names_offsets: int, total_teams: int, base_address: int):
        return [
            Team(
                team_id,
                file_bytes[
                    self.get_name_offset(file_bytes, names_offsets + team_id * 16) - base_address
                    :
                ].partition(b"\0")[0].decode('utf-8'),
                file_bytes[
                    self.get_name_offset(file_bytes, names_offsets + 4 + team_id * 16) - base_address
                    :
                ].partition(b"\0")[0].decode('utf-8'),
            )
            for team_id in range(total_teams)
        ]
    
    def get_nationalities(self, file_bytes: bytes, names_offsets: int, total_teams: int, base_address: int):
        return [
            Nationality(
                nt_id,
                file_bytes[
                    self.get_name_offset(file_bytes, names_offsets + nt_id * 8) - base_address
                    :
                ].partition(b"\0")[0].decode('utf-8'),
                file_bytes[
                    self.get_name_offset(file_bytes, names_offsets + 4 + nt_id * 8) - base_address
                    :
                ].partition(b"\0")[0].decode('utf-8'),
            )
            for nt_id in range(total_teams)
        ]

    def get_stadiums_names(self, file_bytes:bytes, start_offset:int, total_stadiums:int, max_len:int):
        return [
            file_bytes[
                start_offset + stadium_id * max_len
                :
                start_offset + stadium_id * max_len + max_len
            ].partition(b"\0")[0].decode('utf-8')
            for stadium_id in range(total_stadiums)
        ]

    def get_leagues_names(self, file_bytes:bytes, start_offset:int, total:int, max_len:int):
        base_name_len = 20
        record_size = 84
        return [
            file_bytes[
                start_offset + league_id * record_size + base_name_len + 1
                :
                start_offset + league_id * record_size + base_name_len + 1 + max_len 
            ].partition(b"\0")[0].decode('utf-8')
            for league_id in range(total)
        ]

    def get_callnames(self, file_bytes:bytes, lenght:int, encoding:str):
        total_callnames, total_groups, special_callnames, letter_groups = struct.unpack("<4H", file_bytes[32:40])
        start_offset = 40
        record_size = lenght + 8
        for callname in range(total_callnames):
            return [
                Callname(
                    callname,
                    file_bytes[
                        start_offset + (callname * record_size)
                        :
                        start_offset + (callname * record_size) + record_size
                    ],
                    lenght,
                    encoding,
                )
                for callname in range(total_callnames)
            ]

    def write_team_names(self, teams:"list[Team]", base_address:int, start_offset:int, offsets_table:int, data_size:int, file:BinaryFile):
        temp_bytes = bytearray(data_size)
        sum = base_address + start_offset
        sum1 = 0
        for i, team in enumerate(teams):
            name_bytes = team.full_name.encode("utf8","ignore") + bytearray(1)
            abb_bytes = team.abb_name.encode("utf8","ignore") + bytearray(1)
            file.write_bytes(offsets_table + i * 16, struct.pack("<I", sum))
            sum += len(name_bytes)
            file.write_bytes(offsets_table + 4 + i * 16, struct.pack("<I", sum))
            sum += len(abb_bytes)
            team_name_bytes = name_bytes + abb_bytes
            team_name_bytes_size = len(team_name_bytes)
            temp_bytes[sum1 : sum1 + team_name_bytes_size] = team_name_bytes
            sum1 += team_name_bytes_size
        if temp_bytes>data_size:
            raise ValueError("The buffer for the text data its way too big for the reseved space")
        file.write_bytes(start_offset, temp_bytes)

    def write_nt(self, nationalities:"list[Nationality]", base_address:int, start_offset:int, offsets_table:int, data_size:int, file:BinaryFile):
        temp_bytes = bytearray(data_size)
        sum = base_address + start_offset
        sum1 = 0
        for i, nationality in enumerate(nationalities):
            name_bytes = nationality.full_name.encode("utf8","ignore") + bytearray(1)
            abb_bytes = nationality.abb_name.encode("utf8","ignore") + bytearray(1)
            file.write_bytes(offsets_table + i * 8, struct.pack("<I", sum))
            sum += len(name_bytes)
            file.write_bytes(offsets_table + 4 + i * 8, struct.pack("<I", sum))
            sum += len(abb_bytes)
            nationality_bytes = name_bytes + abb_bytes
            nationality_bytes_size = len(nationality_bytes)
            temp_bytes[sum1 : sum1 + nationality_bytes_size] = nationality_bytes
            sum1 += nationality_bytes_size
        if temp_bytes>data_size:
            raise ValueError("The buffer for the text data its way too big for the reseved space")
        file.write_bytes(start_offset, temp_bytes)

    def write_stadiums_names(self, list_of_names:"list[str]", start_offset:int, lenght:int, file:BinaryFile):
        for i, name in enumerate(list_of_names):
            temp_bytes = bytearray(lenght)
            name_bytes = name.encode("utf8","ignore")
            temp_bytes[:len(name_bytes)] = name_bytes
            file.write_bytes(start_offset + i * lenght, temp_bytes)

    def write_leagues_names(self, list_of_names:"list[str]", start_offset:int, lenght:int, file:BinaryFile):
        base_name_len = 20
        record_size = 84
        for i, name in enumerate(list_of_names):
            temp_bytes = bytearray(lenght)
            name_bytes = name.encode("utf8","ignore")
            temp_bytes[:len(name_bytes)] = name_bytes
            file.write_bytes(start_offset + base_name_len + 1 + i * record_size, temp_bytes)

    def write_callnames(self, callnames:"list[Callname]", lenght:int, file:BinaryFile):
        start_offset = 40
        record_size = lenght + 8
        for i, callname in enumerate(callnames):
            file.write_bytes(start_offset + i * record_size, callname.callname_bytes)


