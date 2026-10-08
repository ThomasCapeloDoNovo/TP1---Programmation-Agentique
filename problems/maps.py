from enum import Enum
"""Cartes disponibles.

coords : ville -> (x, y) en km (y vers le nord), sert à l'heuristique et au dessin
roads  : (ville A, ville B, poids). Routes bidirectionnelles.
         Le poids doit être >= distance à vol d'oiseau (heuristique).
"""

class MapsInstance(Enum):
    FRANCE = "France"
    QUEBEC = "Québec"

MAPS = {
    MapsInstance.FRANCE: {
        "coords": {
            "Paris":      (0, 0),
            "Lille":      (30, 205),
            "Reims":      (130, 50),
            "Dijon":      (170, -190),
            "Lyon":       (200, -370),
            "Marseille":  (250, -640),
            "Strasbourg": (416, -32),
            "Toulouse":   (-160, -576),
            "Nantes":     (-256, -192),
            "Rennes":     (-288, -64),
            "Brest":      (-480, -32),
            "Caen":       (-128, 64),
        },
        "roads": [
            ("Paris", "Lille", 225),
            ("Paris", "Reims", 145),
            ("Paris", "Caen", 160),
            ("Paris", "Rennes", 330),         
            ("Paris", "Nantes", 355),         
            ("Paris", "Toulouse", 660),       
            ("Paris", "Strasbourg", 460),     
            ("Brest", "Nantes", 305),         
            ("Brest", "Rennes", 215),         
            ("Nantes", "Toulouse", 440),      
            ("Rennes", "Nantes", 145),        
            ("Rennes", "Caen", 225),          
            ("Caen", "Lille", 235),           
            ("Reims", "Strasbourg", 330),     
            ("Strasbourg", "Dijon", 325),     
            ("Toulouse", "Marseille", 460),   
            ("Toulouse", "Lyon", 450),        
            ("Lille", "Reims", 205),
            ("Reims", "Dijon", 260),
            ("Paris", "Dijon", 315),
            ("Dijon", "Lyon", 195),
            ("Paris", "Lyon", 465),
            ("Lyon", "Marseille", 315),
        ],
        "start": "Lille",
        "goal": "Marseille",
    },
    MapsInstance.QUEBEC: {
        "coords": {
            "Québec":        (0, 0),
            "Montréal":      (-182, -145),
            "Trois-Rivières": (-103, -51),
            "Sherbrooke":    (-52, -157),
            "Saguenay":      (11, 180),
            "Rimouski":      (207, 182),
            "Chibougamau":   (-243, 345),
        },
        "roads": [
            ("Québec", "Trois-Rivières", 130),    
            ("Trois-Rivières", "Montréal", 145),   
            ("Québec", "Sherbrooke", 200),         
            ("Sherbrooke", "Montréal", 155),       
            ("Trois-Rivières", "Sherbrooke", 140), 
            ("Québec", "Saguenay", 210),           
            ("Québec", "Rimouski", 320),           
            ("Saguenay", "Chibougamau", 350),      
            ("Trois-Rivières", "Chibougamau", 480),
        ],
        "start": "Montréal",
        "goal": "Saguenay",
    },
}