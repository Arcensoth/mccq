from mccq.node.data_node import DataNode
from mccq.data_parser.abc.data_parser import DataParser


class V1DataParser(DataParser):
    def _build(self, key: str, node: dict, command: str, command_t: str):
        type_ = node['type']
        executable = node.get('executable')
        redirect = node.get('redirect')
        children = node.get('children', {})

        # whether my command is relevant enough to be rendered
        relevant = executable

        # build my argument string
        if type_ == 'root':
            args = args_t = ()
        elif type_ == 'literal':
            args = args_t = (key,)
        elif type_ == 'argument':
            parser = node['parser'].split(sep=':', maxsplit=1)[1]  # get the `string` from `brigadier:string`
            args = ('<{}>'.format(key),)
            args_t = ('<{}: {}>'.format(key, parser),)
        else:
            args = args_t = ('{}*'.format(key),)

        # argument to provide for parents when collapsing
        argument = args[0] if args else None
        argument_t = args_t[0] if args_t else None

        if redirect:
            # redirect is a list and there may be multiple
            args += ('->', '|'.join(redirect))
            relevant = True

        # special case for `execute run`
        if not (executable or redirect or children):
            args += ('->', '*')
            relevant = True

        # build command
        my_command = ' '.join(arg for arg in ((command or None,) + args) if arg is not None)
        my_command_t = ' '.join(arg_t for arg_t in ((command_t or None,) + args_t) if arg_t is not None)

        # build children, if any
        my_children = tuple(self._build(k, v, my_command, my_command_t) for k, v in children.items())

        # count population
        population = sum(child.population for child in my_children)
        if relevant:
            population += 1

        # build collapsed form
        collapsed = collapsed_t = None
        if my_children:
            collapsed = ' '.join((my_command, '|'.join((child.argument for child in my_children))))
            collapsed_t = ' '.join((my_command_t, '|'.join((child.argument_t for child in my_children))))
            # look for at least one grandchild before appending `...`
            if next((True for child in my_children if child.children), False):
                collapsed += ' ...'
                collapsed_t += ' ...'

        return DataNode(
            relevant=relevant,
            population=population,
            key=key,
            command=my_command,
            command_t=my_command_t,
            argument=argument,
            argument_t=argument_t,
            collapsed=collapsed,
            collapsed_t=collapsed_t,
            children=my_children,
        )

    def parse(self, raw) -> DataNode:
        return self._build('root', raw, '', '')
