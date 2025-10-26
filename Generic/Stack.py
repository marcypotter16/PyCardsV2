from typing import Generic, TypeVar


T = TypeVar('T')


class EmptyStackError(Exception):
    pass


class Stack(Generic[T]):
    def __init__(self):
        self.elements: list[T] = []
        self.__size = 0

    def top(self) -> T:
        """
        Returns the top element of the stack
        :return:
        """
        if self.__size == 0:
            raise EmptyStackError
        return self.elements[0]

    def pop(self) -> T:
        """
        Removes the top element of the stack and returns it
        :return:
        """
        if self.__size == 0:
            raise EmptyStackError
        self.__size -= 1
        return self.elements.pop(0)

    def push(self, obj: T) -> None:
        """
        Adds an element to the top of the stack
        :param obj:
        :return:
        """
        self.elements.insert(0, obj)
        self.__size += 1

    def is_empty(self) -> bool:
        """
        Returns true if the stack is empty
        :return:
        """
        return self.__size == 0

    def size(self) -> int:
        """
        Returns the size of the stack
        :return:
        """
        return self.__size
    
    def __str__(self):
        return str(self.elements)
    
    def to_list(self) -> list[T]:
        return self.elements
