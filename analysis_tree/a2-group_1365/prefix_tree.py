"""CSC148 Assignment 2: Autocompleter classes

=== CSC148 Fall 2018 ===
Department of Computer Science,
University of Toronto

=== Module Description ===
This file contains the design of a public interface (Autocompleter) and two
implementation of this interface, SimplePrefixTree and CompressedPrefixTree.
You'll complete both of these subclasses over the course of this assignment.

As usual, be sure not to change any parts of the given *public interface* in the
starter code---and this includes the instance attributes, which we will be
testing directly! You may, however, add new private attributes, methods, and
top-level functions to this file.
"""
from __future__ import annotations
from typing import Any, List, Optional, Tuple


################################################################################
# The Autocompleter ADT
################################################################################
class Autocompleter:
    """An abstract class representing the Autocompleter Abstract Data Type.
    """

    def __len__(self) -> int:
        """Return the number of values stored in this Autocompleter."""
        raise NotImplementedError

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """Insert the given value into this Autocompleter.

        The value is inserted with the given weight, and is associated with
        the prefix sequence <prefix>.

        If the value has already been inserted into this prefix tree
        (compare values using ==), then the given weight should be *added* to
        the existing weight of this value.

        Preconditions:
            weight > 0
            The given value is either:
                1) not in this Autocompleter
                2) was previously inserted with the SAME prefix sequence
        """
        raise NotImplementedError

    def autocomplete(self, prefix: List,
                     limit: Optional[int] = None) -> List[Tuple[Any, float]]:
        """Return up to <limit> matches for the given prefix.

        The return value is a list of tuples (value, weight), and must be
        ordered in non-increasing weight. (You can decide how to break ties.)

        If limit is None, return *every* match for the given prefix.

        Precondition: limit is None or limit > 0.
        """
        raise NotImplementedError

    def remove(self, prefix: List) -> None:
        """Remove all values that match the given prefix.
        """
        raise NotImplementedError


################################################################################
# SimplePrefixTree (Tasks 1-3)
################################################################################
def _sort_auto_collection(lst: List[Tuple[Any, float]]) -> List[
        Tuple[Any, float]]:
    """
    a helper function used to sort the subtrees in non-increasing order by
    quick sort
    """
    if len(lst) < 2:
        return lst[:]
    else:
        pivot = lst[0][1]
        smaller, bigger = _partition(lst[1:], pivot)

        smaller_sorted = _sort_auto_collection(smaller)
        bigger_sorted = _sort_auto_collection(bigger)

        return bigger_sorted + [lst[0]] + smaller_sorted


def _partition(lst: List[Tuple[Any, float]], pivot: float) -> Tuple[
        List[Tuple[Any, float]], List[Tuple[Any, float]]]:
    """
    a helper function used to partition the list for quick sort
    """
    smaller = []
    bigger = []
    for item in lst:
        if item[1] <= pivot:
            smaller.append(item)
        else:
            bigger.append(item)

    return smaller, bigger


class SimplePrefixTree(Autocompleter):
    """A simple prefix tree.

    This class follows the implementation described on the assignment handout.
    Note that we've made the attributes public because we will be accessing them
    directly for testing purposes.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - ("prefixes grow by 1")
      If len(self.subtrees) > 0, and subtree in self.subtrees, and subtree
      is non-empty and not a leaf, then

          subtree.value == self.value + [x], for some element x

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Any
    weight: float
    subtrees: List[SimplePrefixTree]
    weight_type: str
    _size: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty simple prefix tree.

        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.weight_type = weight_type
        self.weight = 0
        self.subtrees = []
        self.value = []
        self._size = 0

    def __len__(self) -> int:
        """
        used to return the stored length(size) of this tree
        override the magic method __len__
        """
        return self._size

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """
        INSERT method for SimplePrefixTree
        if tree is empty, directly add this value under root [] and update size
        and weight
        else call _insert_helper to insert


        >>> t = SimplePrefixTree('average')
        >>> t.insert("cb", 1, ["c", "b"])
        >>> len(t)
        1
        >>> t.insert("cbd", 1, ["c", "b", "d"])
        >>> len(t)
        2
        >>> t.insert("abd", 1, ["a", "b", "d"])
        >>> t.insert("ac", 1, ["a", "c"])
        >>> t.insert("a", 1, ["a"])
        >>> len(t)
        5
        >>> s = SimplePrefixTree('sum')
        >>> s.insert("ca", 2, ["c", "a"])
        >>> s.insert("cb", 1, ["c", "b"])
        >>> s.insert("cbb", 9999, ["c", "b"])
        >>> s.insert("caa", 4, ["c", "a", "c"])
        >>> s.insert("cab", 3, ["c", "a", "d"])
        >>> s.insert("app", 4000000, [])
        >>> s.subtrees[0].value
        'app'
        >>> s.subtrees[1].subtrees[0].value
        ['c', 'b']
        """
        if self.is_empty():
            self._size += 1
            self.weight = weight
            self._do_insertion(1, prefix, value, weight)
        else:
            self._insert_helper(value, weight, prefix)

    def _insert_helper(self, value: Any, weight: float,
                       prefix: List[Any]) -> bool:
        """
        INSERT while tree is not empty
        loop through the subtrees list,

        if subtree is a leaf, check whether value == subtree,
        if True, simply add weight and redo the size increment then break out

        if subtree is a prefix, recursively do _insert_helper to trace down the
        tree until there's no duplicate prefix path then break set found

        if found is False, go down a level and call _do_insertion
        update weight
        """
        self._size += 1
        found = False
        is_dup = False

        for subtree in self.subtrees:
            if subtree.is_leaf():
                if subtree.value == value:
                    subtree.weight += weight
                    found = True
                    is_dup = True
                    self._size -= 1
                    break
                continue
            elif subtree._is_subprefix(prefix):

                if subtree._insert_helper(value, weight, prefix):
                    self._size -= 1
                    is_dup = True
                found = True
                break

        if not found:
            self._do_insertion(len(self.value) + 1, prefix, value,
                               weight)

        self._add_weight(weight, is_dup)
        self.subtrees.sort(key=SimplePrefixTree._get_weight, reverse=True)

        return is_dup

    def _get_weight(self) -> float:
        """
        return weight
        """
        return self.weight

    def _add_weight(self, weight: float, same_size: bool) -> None:
        """
        update weight
        if sum, simply increment
        if average, calculate a new average after adding value
        """
        if self.weight_type == 'sum':
            self.weight += weight
        elif self.weight_type == 'average':
            if same_size:
                self.weight = (self.weight * len(self) + weight) / len(self)
            else:
                self.weight = ((self.weight * (len(self) - 1) + weight) / len(
                    self))

    def _do_insertion(self, start: int, prefix: List[Any], value: Any,
                      weight: float) -> None:
        """
        from root to the latest parent of value,
        create prefix path by creating tree and appending them to its parent's
        subtrees list and going down level

        finally append created tree containing value to its parent's subtrees
        """
        cur_tree = self

        for k in range(start, len(prefix) + 1):
            new_tree = self._create_tree(prefix[0:k], weight)
            cur_tree.subtrees.append(new_tree)
            cur_tree = new_tree

        cur_tree.subtrees.append(self._create_tree(value, weight))

    def _is_subprefix(self, prefix: List[Any]) -> bool:
        """
        helper method to determine whether value is a sub-prefix of the prefix
        """
        if len(prefix) < len(self.value):
            return False

        for i in range(len(self.value)):
            if self.value[i] != prefix[i]:
                return False
        return True

    def _create_tree(self, value: Any, weight: float) -> SimplePrefixTree:
        """
        helper method to create a tree with simply given value and weight
        """
        tree = SimplePrefixTree(self.weight_type)
        tree.value = value
        tree.weight = weight
        tree._size = 1
        return tree

    def autocomplete(self, prefix: List, limit: Optional[int] = None) -> \
            List[Tuple[Any, float]]:
        """
        AUTOCOMPLETE method
        from root, trace down prefix tree following the corresponding prefix
        path update initial_tree which records current tree
        after loop ended, collect leafs of current tree
        if limitless, call _limitless_leaf_collector()
        else call _limited_leaf_collector(limit) with limit
        >>> t = SimplePrefixTree('average')
        >>> t.insert("ca", 3, ["c", "a"])
        >>> t.insert("cb", 1, ["c", "b"])
        >>> t.insert("cbb", 9999, ["c", "b"])
        >>> t.insert("caa", 2, ["c", "a", "c"])
        >>> t.insert("cab", 4, ["c", "a", "d"])
        >>> t.autocomplete(["c"], None)
        ['cbb', 'cb', 'cab', 'ca', 'caa']
        >>> t.autocomplete(["c"], 3)
        ['cbb', 'cb', 'cab']
        >>> t.autocomplete(["d"], None)
        []
        >>> t.insert("app", 4000000, ["a", "p", "p"])
        >>> t.insert("ask", 1234, [])
        >>> t.autocomplete(["a"], 10)
        ['app']
        """
        if self.is_empty():
            return []

        initial_tree = self

        for k in range(1, len(prefix) + 1):
            lvl_prefix = prefix[0:k]
            found = False

            for subtree in initial_tree.subtrees:
                if subtree.value == lvl_prefix:
                    initial_tree = subtree
                    found = True
                    break

            if not found:
                return []

        if limit is None:
            collected = initial_tree._limitless_leaf_collector()
        else:
            collected = initial_tree._limited_leaf_collector(limit)

        return _sort_auto_collection(collected)

    def _limitless_leaf_collector(self) -> List[Tuple[Any, float]]:
        """
        helper method for limitless leaf collection
        base case: if it's a leaf return tuple of value and weight
        recursive step: for every subtree in current tree's subtrees, call
        leaf collector

        overall, information about all leafs under the given very parent tree
        is returned
        """
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            lst = []
            for subtree in self.subtrees:
                lst.extend(subtree._limitless_leaf_collector())

            return lst

    def _limited_leaf_collector(self, limit: int) -> List[Tuple[Any, float]]:
        """
        helper method for limitless leaf collection
        base case: if it's a leaf return tuple of value and weight
        recursive step: for every subtree in current tree's subtrees, call
        leaf collector

        overall, information about given limit number of leafs under the
        given very parent tree is returned
        """
        if limit <= 0:
            return []
        elif self.is_leaf():
            return [(self.value, self.weight)]
        else:
            lst = []

            for subtree in self.subtrees:
                size = len(subtree)

                if size > limit:
                    lst.extend(subtree._limited_leaf_collector(limit))
                    break
                else:
                    lst.extend(subtree._limitless_leaf_collector())
                    limit -= size

            return lst

    def remove(self, prefix: List[Any]) -> None:
        """
        >>> t = SimplePrefixTree('average')
        >>> t.insert("a", 1, ["a"])
        >>> t.insert("ab", 2, ["a", "b"])
        >>> t.insert("abc", 3, ["a", "b", "c"])
        >>> t.insert("abd", 4, ["a", "b", "d"])
        >>> t.insert("abcd", 5, ["a", "b", "c", "d"])
        >>> t.insert("abcde", 6, ["a", "b", "c", "d", "e"])
        >>> t.remove(["a", "b", "c", "d"])
        >>> t.subtrees[0].subtrees[0].subtrees[0].value
        ['a', 'b', 'd']
        >>> t.subtrees[0].subtrees[0].subtrees[1].weight
        3.0
        >>> t.remove(["a", "b"])
        >>> len(t)
        1
        REMOVE method
        if empty, return
        if is leaf, return

        parent_tree: record latest parent tree
        ancestors: record all trees down in the tracing prefix path
        deleted_tree: store deleted tree

        outer loop through by slice of prefix
        inner loop,
        if found target, remove it from its parent's subtrees
        if not found, store this parent into ancestor and going down one level

        then update each ancestor's size
        find all zombie ancestors (ancestors with size 0
        which means no leaf under it)
        and set weight to 0
        delete them from their parent's subtrees

        update all legal ancestors' weight
        sort all trees involving prefix path again at each level
        since change in subtrees may cause change in weight order
        """
        if self.is_empty():
            return

        if not prefix:
            self.weight = 0
            self.subtrees = []
            self.value = []
            self._size = 0
            return

        parent_tree = self
        ancestors = [self]
        found = False
        deleted_tree = None

        for k in range(1, len(prefix) + 1):
            lvl_prefix = prefix[0:k]

            for subtree in parent_tree.subtrees:
                if subtree.value == prefix:
                    deleted_tree = subtree
                    parent_tree.subtrees.remove(subtree)
                    found = True
                    break

                if subtree.value == lvl_prefix:
                    ancestors.append(subtree)
                    parent_tree = subtree
                    break

        if not found or deleted_tree is None:
            return

        zombie_ancestor = None
        for ancestor in reversed(ancestors):
            ancestor._size -= len(deleted_tree)

            if ancestor._size == 0:
                zombie_ancestor = ancestor
                ancestor.weight = 0
                continue
            else:
                if zombie_ancestor is not None:
                    ancestor.subtrees.remove(zombie_ancestor)
                    zombie_ancestor = None

            if self.weight_type == 'average':
                sum_ = 0
                count = 0
                for subtree in ancestor.subtrees:
                    sum_ += subtree.weight * len(subtree)
                    count += len(subtree)
                ancestor.weight = sum_ / count
            elif self.weight_type == 'sum':
                ancestor.weight -= deleted_tree.weight

            ancestor.subtrees.sort(key=SimplePrefixTree._get_weight,
                                   reverse=True)

    def is_empty(self) -> bool:
        """Return whether this simple prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this simple prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s


################################################################################
# CompressedPrefixTree (Task 6)
################################################################################
def _is_sublist(large: List[Any], small: List[Any]) -> bool:
    """
    helper method used to determine sub-prefix relationship
    """
    for i in range(len(small)):
        if large[i] != small[i]:
            return False

    return True


class CompressedPrefixTree(Autocompleter):
    """A compressed prefix tree implementation.

    While this class has the same public interface as SimplePrefixTree,
    (including the initializer!) this version follows the implementation
    described on Task 6 of the assignment handout, which reduces the number of
    tree objects used to store values in the tree.

    === Attributes ===
    value:
        The value stored at the root of this prefix tree, or [] if this
        prefix tree is empty.
    weight:
        The weight of this prefix tree. If this tree is a leaf, this attribute
        stores the weight of the value stored in the leaf. If this tree is
        not a leaf and non-empty, this attribute stores the *aggregate weight*
        of the leaf weights in this tree.
    subtrees:
        A list of subtrees of this prefix tree.

    === Representation invariants ===
    - self.weight >= 0

    - (EMPTY TREE):
        If self.weight == 0, then self.value == [] and self.subtrees == [].
        This represents an empty simple prefix tree.
    - (LEAF):
        If self.subtrees == [] and self.weight > 0, this tree is a leaf.
        (self.value is a value that was inserted into this tree.)
    - (NON-EMPTY, NON-LEAF):
        If len(self.subtrees) > 0, then self.value is a list (*common prefix*),
        and self.weight > 0 (*aggregate weight*).

    - **NEW**
      This tree does not contain any compressible internal values.
      (See the assignment handout for a definition of "compressible".)

    - self.subtrees does not contain any empty prefix trees.
    - self.subtrees is *sorted* in non-increasing order of their weights.
      (You can break ties any way you like.)
      Note that this applies to both leaves and non-leaf subtrees:
      both can appear in the same self.subtrees list, and both have a `weight`
      attribute.
    """
    value: Optional[Any]
    weight: float
    subtrees: List[CompressedPrefixTree]
    weight_type: str
    _size: int

    def __init__(self, weight_type: str) -> None:
        """Initialize an empty compressed prefix tree.
        Precondition: weight_type == 'sum' or weight_type == 'average'.

        The given <weight_type> value specifies how the aggregate weight
        of non-leaf trees should be calculated (see the assignment handout
        for details).
        """
        self.value = []
        self.weight = 0
        self.subtrees = []
        self.weight_type = weight_type
        self._size = 0

    def __len__(self) -> int:
        """
        helper method return size of tree
        """
        return self._size

    def insert(self, value: Any, weight: float, prefix: List) -> None:
        """
        INSERT method for SimplePrefixTree
        if tree is empty, directly add this value under root [] and update size
        and weight
        else call _insert_helper to insert
        """
        if self.is_empty():
            self._size += 1
            self.weight = weight
            self._do_insertion(prefix, value, weight)
        else:
            self._insert_helper(value, weight, prefix)

    def _insert_helper(self, value: Any, weight: float,
                       prefix: List[Any]) -> bool:

        """
        INSERT while tree is not empty
        loop through the subtrees list,

        if subtree is a leaf, check whether value == subtree,
        if True, simply add weight and redo the size increment then break out

        if subtree is a prefix, recursively do _insert_helper to trace down the
        tree until there's no duplicate prefix path then break set found

        if found is False, go down a level and call _do_insertion
        update weight
        """
        self._size += 1
        found = False
        is_dup = False

        for subtree in self.subtrees:
            if subtree.is_leaf():
                if subtree.value == value:
                    subtree.weight += weight
                    found = True
                    is_dup = True
                    self._size -= 1
                    break
                continue
            elif subtree._is_subprefix(prefix):

                if subtree._insert_helper(value, weight, prefix):
                    self._size -= 1
                    is_dup = True
                found = True
                break

        if not found:
            self._do_insertion(prefix, value, weight)

        self._add_weight(weight, is_dup)
        self.subtrees.sort(key=CompressedPrefixTree._get_weight, reverse=True)

        return is_dup

    def _get_weight(self) -> float:
        """
        helper method used to get tree's weight
        """
        return self.weight

    def _add_weight(self, weight: float, same_size: bool) -> float:
        """
        helper method to add weight according to weight_type
        """
        if self.weight_type == 'sum':
            self.weight += weight
        elif self.weight_type == 'average':
            if same_size:
                self.weight = (self.weight * len(self) + weight) / len(self)
            else:
                self.weight = ((self.weight * (len(self) - 1) + weight) / len(
                    self))

        return self.weight

    def _do_insertion(self, prefix: List[Any], value: Any,
                      weight: float) -> None:
        """
        compressed version of _do_insertion
        ignore all the shared part by help of _count_share
        """
        for subtree in self.subtrees:
            share = subtree._count_share(prefix)

            if share > len(self.value):
                new_pref = prefix[0:share]

                if self.weight_type == 'average':
                    new_weight = (subtree.weight *
                                  (len(subtree) - 1) + weight) / len(subtree)
                else:
                    new_weight = subtree.weight + weight

                new_parent = self._create_tree(new_pref, new_weight)
                new_parent.subtrees.append(subtree)
                self.subtrees.remove(subtree)
                new_parent.subtrees.append(
                    self._get_last_parent(prefix, value, weight))
                new_parent._size += 1
                self.subtrees.append(new_parent)
                return

        self.subtrees.append(self._get_last_parent(prefix, value, weight))

    def _get_last_parent(self, prefix: List[Any], value: Any,
                         weight: float) -> CompressedPrefixTree:
        """
        helper method getting latest parent tree by create a same one by prefix
        """
        parent = self._create_tree(prefix, weight)
        leaf = self._create_tree(value, weight)
        parent.subtrees.append(leaf)
        return parent

    def _count_share(self, prefix: List[Any]) -> int:
        """
        return the count of the length of shared part of prefix and value
        """
        if len(self.value) < len(prefix):
            return 0

        count = 0
        for i in range(len(prefix)):
            if prefix[i] == self.value[i]:
                count += 1
            else:
                break
        return count

    def _is_subprefix(self, prefix: List[Any]) -> bool:
        """
        helper method determining sub-prefix relationship
        """
        if len(prefix) < len(self.value):
            return False

        for i in range(len(self.value)):
            if self.value[i] != prefix[i]:
                return False
        return True

    def _create_tree(self, value: Any, weight: float) -> CompressedPrefixTree:
        """
        helper method to create a tree simply with given value and weight
        """
        tree = CompressedPrefixTree(self.weight_type)
        tree.value = value
        tree.weight = weight
        tree._size = 1
        return tree

    def autocomplete(self, prefix: List[Any], limit: Optional[int] = None) -> \
            List[Tuple[Any, float]]:
        """
         AUTOCOMPLETE method
        from root, trace down prefix tree following the corresponding prefix
        path update initial_tree which records current tree
        after loop ended, collect leafs of current tree
        if limitless, call _limitless_leaf_collector()
        else call _limited_leaf_collector(limit) with limit
        """
        if self.is_empty():
            return []

        initial_tree = self._find_initial_tree(prefix)

        if initial_tree is None:
            return []

        if limit is None:
            collected = initial_tree._limitless_leaf_collector()
        else:
            collected = initial_tree._limited_leaf_collector(limit)

        return _sort_auto_collection(collected)

    def _find_initial_tree(self, prefix: List[Any]) -> Optional[
            CompressedPrefixTree]:
        """
        helper method finding the initial tree
        """
        for subtree in self.subtrees:
            if subtree.is_leaf():
                continue

            if len(subtree.value) >= len(prefix) and _is_sublist(subtree.value,
                                                                 prefix):
                return subtree

            elif len(subtree.value) < len(prefix) and \
                    _is_sublist(prefix, subtree.value):
                return subtree._find_initial_tree(prefix)

        return None

    def _limitless_leaf_collector(self) -> List[Tuple[Any, float]]:
        """
        helper method for limitless leaf collection
        base case: if it's a leaf return tuple of value and weight
        recursive step: for every subtree in current tree's subtrees, call
        leaf collector

        overall, information about all leafs under the
        given very parent tree is returned
        """
        if self.is_leaf():
            return [(self.value, self.weight)]
        else:
            lst = []
            for subtree in self.subtrees:
                lst.extend(subtree._limitless_leaf_collector())

            return lst

    def _limited_leaf_collector(self, limit: int) -> List[Tuple[Any, float]]:
        """
        helper method for limitless leaf collection
        base case: if it's a leaf return tuple of value and weight
        recursive step: for every subtree in current tree's subtrees, call
        leaf collector

        overall, information about given limit number of leafs under the
        given very parent tree is returned
        """
        if limit <= 0:
            return []
        elif self.is_leaf():
            return [(self.value, self.weight)]
        else:
            lst = []

            for subtree in self.subtrees:
                size = len(subtree)

                if size > limit:
                    lst.extend(subtree._limited_leaf_collector(limit))
                    break
                else:
                    lst.extend(subtree._limitless_leaf_collector())
                    limit -= size

            return lst

    def _get_deletion_info(self, prefix: List[Any]) -> Optional[Tuple[
            List[CompressedPrefixTree], CompressedPrefixTree,
            CompressedPrefixTree]]:
        """
        get the deletion info
        """
        for subtree in self.subtrees:
            if subtree.is_leaf():
                continue

            if len(subtree.value) >= len(prefix) and _is_sublist(subtree.value,
                                                                 prefix):
                return [subtree], subtree, self

            elif len(subtree.value) < len(prefix) and \
                    _is_sublist(prefix, subtree.value):
                result = subtree._get_deletion_info(prefix)

                if result is None:
                    return None

                result[0].append(subtree)
                return result[0], result[1], result[2]

        return None

    def remove(self, prefix: List[Any]) -> None:
        """
        REMOVE method
        if empty, return
        if is leaf, return

        parent_tree: record latest parent tree
        ancestors: record all trees down in the tracing prefix path
        deleted_tree: store deleted tree

        outer loop through by slice of prefix
        inner loop,
        if found target, remove it from its parent's subtrees
        if not found, store this parent into ancestor and going down one level

        then update each ancestor's size
        find all zombie ancestors (ancestors with size 0
        which means no leaf under it)
        and set weight to 0
        delete them from their parent's subtrees

        update all legal ancestors' weight
        sort all trees involving prefix path again at each level
        since change in subtrees may cause change in weight order
        """
        if self.is_empty():
            return

        if not prefix:
            self.weight = 0
            self.subtrees = []
            self.value = None
            self._size = 0
            return

        deletion_info = self._get_deletion_info(prefix)

        if deletion_info is None:
            return

        ancestors = [self] + deletion_info[0]
        deleted_tree = deletion_info[1]

        deletion_info[2].subtrees.remove(deletion_info[1])

        zombie_ancestor = None
        for ancestor in reversed(ancestors):
            ancestor._size -= len(deleted_tree)

            if ancestor._size == 0:
                zombie_ancestor = ancestor
                ancestor.weight = 0
                continue
            else:
                if zombie_ancestor is not None:
                    ancestor.subtrees.remove(zombie_ancestor)
                    zombie_ancestor = None

            if self.weight_type == 'average':
                sum_ = 0
                count = 0
                for subtree in ancestor.subtrees:
                    sum_ += subtree.weight * len(subtree)
                    count += len(subtree)
                ancestor.weight = sum_ / count
            elif self.weight_type == 'sum':
                ancestor.weight -= deleted_tree.weight

            ancestor.subtrees.sort(key=CompressedPrefixTree._get_weight,
                                   reverse=True)

    def is_empty(self) -> bool:
        """Return whether this compressed prefix tree is empty."""
        return self.weight == 0.0

    def is_leaf(self) -> bool:
        """Return whether this compressed prefix tree is a leaf."""
        return self.weight > 0 and self.subtrees == []

    def __str__(self) -> str:
        """Return a string representation of this tree.

        You may find this method helpful for debugging.
        """
        return self._str_indented()

    def _str_indented(self, depth: int = 0) -> str:
        """Return an indented string representation of this tree.

        The indentation level is specified by the <depth> parameter.
        """
        if self.is_empty():
            return ''
        else:
            s = '  ' * depth + f'{self.value} ({self.weight})\n'
            for subtree in self.subtrees:
                s += subtree._str_indented(depth + 1)
            return s


if __name__ == '__main__':
    # import doctest
    #
    # doctest.testmod()

    import python_ta

    python_ta.check_all(config={
        'max-nested-blocks': 4
    })
