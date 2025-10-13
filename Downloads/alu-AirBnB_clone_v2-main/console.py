#!/usr/bin/python3
"""
Console module for the AirBnB clone project.
"""
import cmd
import re
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """
    Command interpreter for the AirBnB clone project.
    """
    prompt = "(hbnb) "

    classes = {
        'BaseModel': BaseModel,
        'User': User,
        'State': State,
        'City': City,
        'Amenity': Amenity,
        'Place': Place,
        'Review': Review
    }

    def do_quit(self, arg):
        """
        Quit command to exit the program.
        """
        return True

    def do_EOF(self, arg):
        """
        EOF command to exit the program.
        """
        print()
        return True

    def emptyline(self):
        """
        Do nothing on empty line.
        """
        pass

    def do_create(self, arg):
        """
        Create a new instance of a class with optional parameters.
        Usage: create <Class name> <param 1> <param 2> <param 3>...
        Param syntax: <key name>=<value>
        """
        if not arg:
            print("** class name missing **")
            return

        args = arg.split()
        class_name = args[0]

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        # Create instance with parameters
        kwargs = {}

        for param in args[1:]:
            if '=' not in param:
                continue

            key, value = param.split('=', 1)

            # Parse value based on type
            try:
                # String value (starts and ends with quotes)
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]  # Remove quotes
                    value = value.replace('_', ' ')  # Replace _
                    value = value.replace('\\"', '"')  # Unescape
                # Float value (contains a dot)
                elif '.' in value:
                    value = float(value)
                # Integer value
                else:
                    value = int(value)

                kwargs[key] = value
            except (ValueError, TypeError):
                # Skip invalid parameters
                continue

        # Create instance
        new_instance = self.classes[class_name](**kwargs)
        new_instance.save()
        print(new_instance.id)

    def do_show(self, arg):
        """
        Show string representation of an instance.
        Usage: show <Class name> <id>
        """
        args = arg.split()

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        obj_id = args[1]
        key = "{}.{}".format(class_name, obj_id)

        all_objs = storage.all()
        if key in all_objs:
            print(all_objs[key])
        else:
            print("** no instance found **")

    def do_destroy(self, arg):
        """
        Delete an instance based on the class name and id.
        Usage: destroy <Class name> <id>
        """
        args = arg.split()

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        obj_id = args[1]
        key = "{}.{}".format(class_name, obj_id)

        all_objs = storage.all()
        if key in all_objs:
            obj = all_objs[key]
            storage.delete(obj)
            storage.save()
        else:
            print("** no instance found **")

    def do_all(self, arg):
        """
        Print string representation of all instances or of a specific class.
        Usage: all [Class name]
        """
        args = arg.split()
        obj_list = []

        if args:
            class_name = args[0]
            if class_name not in self.classes:
                print("** class doesn't exist **")
                return
            all_objs = storage.all(self.classes[class_name])
        else:
            all_objs = storage.all()

        for obj in all_objs.values():
            obj_list.append(str(obj))

        print(obj_list)

    def do_update(self, arg):
        """
        Update an instance based on the class name and id.
        Usage: update <Class name> <id> <attribute name> "<attribute value>"
        """
        args = arg.split()

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        if len(args) < 2:
            print("** instance id missing **")
            return

        obj_id = args[1]
        key = "{}.{}".format(class_name, obj_id)

        all_objs = storage.all()
        if key not in all_objs:
            print("** no instance found **")
            return

        if len(args) < 3:
            print("** attribute name missing **")
            return

        if len(args) < 4:
            print("** value missing **")
            return

        obj = all_objs[key]
        attr_name = args[2]
        attr_value = args[3]

        # Remove quotes if present
        if attr_value.startswith('"') and attr_value.endswith('"'):
            attr_value = attr_value[1:-1]

        # Try to cast to appropriate type
        if hasattr(obj, attr_name):
            attr_type = type(getattr(obj, attr_name))
            try:
                attr_value = attr_type(attr_value)
            except (ValueError, TypeError):
                pass

        setattr(obj, attr_name, attr_value)
        obj.save()

    def do_count(self, arg):
        """
        Count the number of instances of a class.
        Usage: count <Class name>
        """
        args = arg.split()

        if not args:
            print("** class name missing **")
            return

        class_name = args[0]

        if class_name not in self.classes:
            print("** class doesn't exist **")
            return

        all_objs = storage.all(self.classes[class_name])
        print(len(all_objs))


if __name__ == '__main__':
    HBNBCommand().cmdloop()
