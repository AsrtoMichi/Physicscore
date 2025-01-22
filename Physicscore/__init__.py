from Physicscore.src import generate_report, Physicscore

__all__ = ["physicscore", "reportgen"]

def physicscore():
    Physicscore().mainloop()

def reportgen():
    generate_report()
