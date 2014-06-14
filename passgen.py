#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 17.07.2011
@author: s0rg
'''
import re
import sys
import random
import simplejson as json


class Char(object):
    '''
    Password char container, defines 'role' and 'chars',
    where:
        'role'  - type of char
        'chars' - list of char representations
    '''
    def __init__(self, role, *chars):
        self.role = role
        self.chars = chars

    def get(self):
        '''
        Returns one of the 'chars'
        '''
        return random.choice(self.chars)

    def __repr__(self):
        return '<Char({})>'.format(', '.join(self.chars))



class Rule(object):
    '''
    Password-generator rule, contains set of char roles.
    '''
    def __init__(self, rule):
        self.rule = rule

    def match(self, pattern):
        '''
        Matches Rule against list of Chars
        '''
        r, p = self.rule, pattern
        len_p, len_r = len(p), len(r)

        if len_p >= len_r:
            r = self.rule[:-1]
            p = pattern[-len(r):]
        elif len_p < len_r:
            r = self.rule[:len_p]

        return all(map(lambda a, b: a == b.role, r, p))

    def __getitem__(self, index):
        return self.rule[index]

    def __repr__(self):
        return '<PasswordRule({})>'.format(', '.join(self.rule))



def _load_alphabet(roles, chars):
    for c in chars:
        if c['role'] not in roles:
            raise Exception('InvalidRoleName: "{}"'.format(c['role']))
        yield Char(c['role'], *c['chars'])


def _load_rules(rules):
    rules_re = re.compile('{(.*?)}')
    for r in rules:
        items = rules_re.findall(r)
        if not items:
            raise Exception('InvalidRuleFormat: "{}"'.format(r))
        yield Rule(items)


def load_config(config):
    with open(config) as fd:
        cfg = json.load(fd)

    roles = cfg['roles']
    chars = cfg['chars']
    rules = cfg['rules']

    alphabet = list(_load_alphabet(roles, chars))
    rules = list(_load_rules(rules))

    return alphabet, rules


class PasswordGenerator(object):

    def __init__(self, alphabet, rules):
        self.rules = rules
        self.alphabet = alphabet

    def get_char(self, role):
        chars = [c for c in self.alphabet if c.role == role]
        return random.choice(chars)

    def find_role(self, password):
        if not password:
            rule = random.choice(self.rules)
            return rule[0]

        rules = [r for r in self.rules if r.match(password)]
        rule = random.choice(rules)
        return rule[-1]

    def make_chars(self, char_count):
        chars = []
        while len(chars) != char_count:
            role = self.find_role(chars)
            char = self.get_char(role)
            chars.append(char)
            yield char

    def make_one(self, min_len, max_len):
        pass_len = random.randrange(min_len, max_len + 1)
        return ''.join([c.get() for c in self.make_chars(pass_len)])

    def make_many(self, min_len, max_len, how_much):
        for _ in range(how_much):
            yield self.make_one(min_len, max_len)


def create_generator(config):
    alphabet, rules = load_config(config)
    return PasswordGenerator(alphabet, rules)


if __name__ == "__main__":

    import optparse

    def parse_opts(argv):
        parser = optparse.OptionParser()
        parser.add_option('--min', action='store', dest='min_len',
                          type='int', default=8)
        parser.add_option('--max', action='store', dest='max_len',
                          type='int', default=12)
        parser.add_option('--count', action='store', dest='count',
                          type='int', default=10)
        parser.add_option('--config', action='store', dest='config',
                          default='default.json')

        o, _ = parser.parse_args(argv)
        return o

    def main(argv):
        opts = parse_opts(argv)

        pg = create_generator(opts.config)
        for password in pg.make_many(opts.min_len, opts.max_len, opts.count):
            print('{} [{}]'.format(password, len(password)))

        return 0

    sys.exit(main(sys.argv))

