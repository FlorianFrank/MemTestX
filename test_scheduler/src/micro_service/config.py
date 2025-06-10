import dataclasses
from abc import ABC
from dataclasses import dataclass

#from db.DBAdapter import TableField, DBAdapter


@dataclass
class Config(ABC):
    """
    Superclass for all configurations, including configs for tests, post processors, exporters, importer and
    visualizers. This superclass does nothing yet, though this may change in the future.
    """

    @property
    def db_table_name(self) -> str:
        raise ValueError('')

    @property
    def db_table_scheme(self): # -> list[TableField]:
        raise ValueError('')

    def db_tuple(self) -> tuple[tuple, tuple]:
        keys = ()
        values = ()
        self_dict: dict = dataclasses.asdict(self)
        for field in self.db_table_scheme[1:]:  # Skip configId
            keys += (field.name,)
            values += (self_dict.get(field.name, 'NULL'),)

        return keys, values

    def config_id(self, db_adapter) -> int:
        identifier_tuple = self.db_tuple()
        where_query = db_adapter.build_where_query(list(identifier_tuple[0]), list(identifier_tuple[1]))
        return db_adapter.query(f'SELECT MAX(configId) FROM {self.db_table_name} WHERE {where_query}')[0][0]

    #def db_export(self, db_adapter: DBAdapter) -> int:
     #   db_adapter.create_table(self.db_table_name, self.db_table_scheme)

        config_id = self.config_id(db_adapter)

        if config_id is None:  # Config not yet in table
            config_id = self.__get_next_config_id(db_adapter)
            query = f'INSERT INTO {self.db_table_name} VALUES {(config_id,) + self.db_tuple()[1]}'
            db_adapter.query(db_adapter.clean_insert_query(query))

        return config_id

    @classmethod
    #def db_import(cls, db_adapter: DBAdapter, config_id: int) -> 'Config':
     #   row = db_adapter.query(f'SELECT * FROM {cls.db_table_name} WHERE configId = {config_id}')[0]
      #  return cls(*row[1:])

    def __get_next_config_id(self, db_adapter) -> int:
        max_id = db_adapter.query(f'SELECT MAX(configId) FROM {self.db_table_name}')[0][0]
        return 0 if max_id is None else max_id + 1
