def get_character(book):
  if book == "bible":
    return "Angela"
  elif book == "davinci":
    return "Phyllis"
  elif book == "hp":
    return "Dwight"
  else:
    return None
  
def get_gif(character):
  if character == "Angela":
    return "https://media.giphy.com/media/Vew93C1vI2ze/giphy.gif"
  elif character == "Phyllis":
    return "https://media.giphy.com/media/1oGnY1ZqXb123IDO4a/giphy.gif"
  elif character == "Dwight":
    return "https://media.giphy.com/media/Cz1it5S65QGuA/giphy.gif"
  else:
    return None