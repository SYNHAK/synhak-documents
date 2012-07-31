from __future__ import division
import gzip
import xml.dom.minidom as dom

class XMLNode(object):
    def __init__(self, node):
        self._node = node

    def tagContents(self, tagName):
        node = self._node.getElementsByTagName(tagName)[0]
        node.normalize()
        return node.childNodes[0].data

    @property
    def node(self):
        return self._node

class Book(object):
    def __init__(self, fh):
        self._f = gzip.GzipFile(fh)
        self._dom = dom.parse(self._f)
        self._accounts = map(lambda a:XMLAccount(self, a), self._dom.getElementsByTagName("gnc:account"))
        self._transactions = map(lambda t:XMLTransaction(self, t), self._dom.getElementsByTagName("gnc:transaction"))

    @property
    def accounts(self):
        return self._accounts

    @property
    def transactions(self):
        return self._transactions

    def account(self, guid):
        for a in self.accounts:
            if a.id == guid:
                return a

class Account(object):
    def __init__(self, book):
        self.__book = book

    @property
    def book(self):
        return self.__book

    @property
    def transactions(self):
        for trans in self.book.transactions:
            if reduce(lambda x,y:x or self == y.account, trans.splits):
                yield trans

    @property
    def children(self):
        ret = []
        for acct in self.book.accounts:
            if acct.parent == self:
                yield acct

    @property
    def value(self):
        ret = Value()
        for trans in self.transactions:
            for split in trans.splits:
                if split.account == self:
                    ret = split.value + ret
        for c in self.children:
            ret = c.value + ret
        return ret

class XMLAccount(Account, XMLNode):
    def __init__(self, book, node):
        super(XMLAccount, self).__init__(book)
        self._node = node
        try:
            self._parent = AccountReference(self.tagContents("act:parent"), book)
        except IndexError:
            self._parent = None

    @property
    def id(self):
        id = self._node.getElementsByTagName("act:id")[0]
        id.normalize()
        return id.childNodes[0].data

    @property
    def name(self):
        name = self._node.getElementsByTagName("act:name")[0]
        name.normalize()
        return name.childNodes[0].data

    @property
    def parent(self):
        return self._parent

    def __str__(self):
        return self.name

class AccountReference(Account):
    def __init__(self, guid, book):
        super(AccountReference, self).__init__(book)
        self._guid = guid

    def __getattr__(self, name):
        return getattr(self.book.account(guid=self._guid), name)

    def __eq__(self, other):
        return self._guid == other.id

class Transaction(object):
    def __init__(self, book):
        self._book = book

    @property
    def book(self):
        return self._book

    @property
    def splits(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError

class XMLTransaction(Transaction):
    def __init__(self, book, node):
        super(XMLTransaction, self).__init__(book)
        self._node = node
        self._splits = map(lambda s:XMLSplit(self.book, s), self._node.getElementsByTagName("trn:split"))

    @property
    def description(self):
        desc = self._node.getElementsByTagName("trn:description")[0]
        desc.normalize()
        return desc.childNodes[0].data
    
    @property
    def splits(self):
        return self._splits

class Split(object):
    def __init__(self, book):
        self.__book = book

    @property
    def book(self):
        return self.__book

    @property
    def value(self):
        raise NotImplementedError

class XMLSplit(Split):
    def __init__(self, book, node):
        super(XMLSplit, self).__init__(book)
        self._node = node
        valueNode = self._node.getElementsByTagName("split:value")[0]
        valueNode.normalize()
        numerator, denomerator = map(int, valueNode.childNodes[0].data.split('/'))
        self._value = Value(numerator, denomerator)
        acctNode = self._node.getElementsByTagName("split:account")[0]
        acctNode.normalize()
        uuid = acctNode.childNodes[0].data
        self._account = self.book.account(guid=uuid)

    @property
    def value(self):
        return self._value

    @property
    def account(self):
        return self._account

class Value(object):
    def __init__(self, num=None, denom=None):
        self.num = num
        self.denom = denom

    def __add__(self, other):
        if (self.num is None):
            return other
        if (isinstance(other, Value)):
            if (self.denom == other.denom):
                return Value(self.num+other.num, self.denom)
        if other == 0 or other is None or other.denom is None:
            return self
        if self.denom is None:
            return other
        return NotImplemented

    def __iadd__(self, other):
        if self.num is None:
            return other
        if (isinstance(other, Value)):
            if (self.denom == other.denom):
                self.num += other.num
                return self
        if other == 0 or other is None or other.denom is None:
            return self
        if self.denom is None:
            return other
        return NotImplemented

    def __repr__(self):
        return "Value(%s, %s)"%(self.num, self.denom)

    def __str__(self):
        if self.denom == 0 or self.denom is None:
            return "0"
        return str(int(self.num)/int(self.denom))
