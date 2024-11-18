from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date, JSON, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StationStats(Base):
    __tablename__ = "station_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stationID = Column(Integer, nullable=False)  # Foreign Key can be defined in relationships
    measurementDate = Column(Date, nullable=False)

    minAirT = Column(Float, nullable=True)
    maxAirT = Column(Float, nullable=True)
    meanAirT = Column(Float, nullable=True)

    minAirH = Column(Float, nullable=True)
    maxAirH = Column(Float, nullable=True)
    meanAirH = Column(Float, nullable=True)

    sumRain = Column(Float, nullable=True)

    minWindS = Column(Float, nullable=True)
    maxWindS = Column(Float, nullable=True)
    meanWindS = Column(Float, nullable=True)

    minSoilT = Column(Float, nullable=True)
    maxSoilT = Column(Float, nullable=True)
    meanSoilT = Column(Float, nullable=True)

    minSoilVWC = Column(Float, nullable=True)
    maxSoilVWC = Column(Float, nullable=True)
    meanSoilVWC = Column(Float, nullable=True)

    minSoilEC = Column(Float, nullable=True)
    maxSoilEC = Column(Float, nullable=True)
    meanSoilEC = Column(Float, nullable=True)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"<StationStats(id={self.id}, stationID={self.stationID}, "
            f"measurementDate={self.measurementDate})>"
        )


class Pests(Base):
    __tablename__ = "pests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Setting length for VARCHAR
    scientificName = Column(String(255), nullable=True)
    russianName = Column(String(255), nullable=True)
    uzbekName = Column(String(255), nullable=True)

    startWeekOfYear = Column(Integer, nullable=True)
    endWeekOfYear = Column(Integer, nullable=True)

    startTemperature = Column(Float, nullable=True)
    endTemperature = Column(Float, nullable=True)
    baseTemperature = Column(Float, nullable=True)
    maxTemperature = Column(Float, nullable=True)
    hatchingTemperature = Column(Float, nullable=True)
    larvaEntryTemperature = Column(Float, nullable=True)
    larvaExitTemperature = Column(Float, nullable=True)
    deathTemperature = Column(Float, nullable=True)
    totalTemperature = Column(Float, nullable=True)
    idealTemperature = Column(Float, nullable=True)
    idealHumidity = Column(Float, nullable=True)

    fullCycleInDays = Column(Integer, nullable=True)
    numOfCyclesPerYear = Column(Integer, nullable=True)

    description = Column(Text, nullable=True)  # Text does not require a length
    chemicalTreatment = Column(Text, nullable=True)
    nonChemicalTreatment = Column(Text, nullable=True)

    isPest = Column(Boolean, nullable=True)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"<Pests(id={self.id}, name={self.name}, scientificName={self.scientificName}, "
            f"startWeekOfYear={self.startWeekOfYear}, endWeekOfYear={self.endWeekOfYear})>"
        )


class Models(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # Setting length for VARCHAR

    settings = Column(JSON, nullable=True)

    isDefault = Column(Boolean, nullable=False)
    isPest = Column(Boolean, nullable=True)

    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return (
            f"<Models(id={self.id}, name={self.name}"
        )
