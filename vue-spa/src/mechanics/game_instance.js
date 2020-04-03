import {Hero, Unit, Structure} from './game_objects';
import HexGrid from './grid';
import ActionManager from './actions';

const colors = {
    'tileBackground': '#f0e256',
    'heroMoves': '#5D8AAD',
    'unitMoves': '#EE5A3A',
    'crossMoves': '#E1330D',  // unit's and hero's moves intersection
    'target': '#0f7cdb'
}

class GameInstance {
    /**
    * Class to work with game board
    */
    constructor(component, svg_field, game_data) {
        this.component = component;
        this.svg = svg_field;
        this.grid = new HexGrid(this, game_data.board);

        this.hero = new Hero(this, game_data.hero);
        this.units = {};
        this.structures = {};
        for (var structure_id in game_data.structures) {
            this.structures[structure_id] = new Structure(this, game_data.structures[structure_id]);
        }
        for (var unit_id in game_data.units) {
            this.units[unit_id] = new Unit(this, game_data.units[unit_id]);
        }

        this.actionManager = new ActionManager(this);
        this.actionManager.setAction('move');

        this.current_unit = false;
        this.show_unit_card = false;  // variable for UnitCard element in Vue component
        this.altPressed = false;
    }

    handleAction(response) {
        console.log('response', response);
        if (response.action_data.state != 'success') {
            this.actionManager.changeAction('move');
        } else {
            this.grid.update_hexes(response.board.hexes);
            this.hero.update(response.hero, response.action_data.hero_actions);
            this.update_units(response.units, response.action_data.units_actions);
            this.actionManager.changeAction('move');
        }
    }

    update_units(new_units, units_actions) {
        let units_to_add = Object.keys(new_units).filter(u => !(u in this.units));
        let units_to_update = Object.keys(this.units).filter(u => u in new_units);
        let units_to_remove = Object.keys(this.units).filter(u => !(u in new_units));

        units_to_remove.forEach(unit_id => {
            this.units[unit_id].image.remove();
            delete this.units[unit_id];
        });
        units_to_add.forEach(unit_id => {
            this.units[unit_id] = new Unit(this, new_units[unit_id]);
        });
        units_to_update.forEach(unit_id => {
            this.units[unit_id].update(new_units[unit_id], units_actions[unit_id]);
        });
    }

    getUnitByHex(_hex) {
        if (this.hero.hex == _hex) {
            return this.hero;
        }
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            if (unit.hex == _hex) {
                return unit;
            }
        };
    }

    showMoves() {
        this.hero.moves.forEach(hex_id => {
            document.getElementById(hex_id).setAttribute('fill', colors.heroMoves);
        });
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex_id => {
                document.getElementById(hex_id)
                    .setAttribute('fill', this.hero.moves.includes(hex_id) ? colors.crossMoves : colors.unitMoves);
            })
        };
        this.grid.coordinates.attr('display', '');
    }

    hideMoves() {
        for (var unit_id in this.units) {
            let unit = this.units[unit_id];
            unit.attack_hexes.forEach(hex_id => {
                this.grid.hexes[hex_id].setCurrentBackground();
            })
        };
        this.hero.moves.forEach(hex_id => {
            this.grid.hexes[hex_id].setCurrentBackground();
        });
        this.grid.coordinates.attr('display', 'none');
    }
}

export default GameInstance
